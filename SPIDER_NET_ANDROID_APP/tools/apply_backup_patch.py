#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / "app/src/main/java/com/spidernet/accounting/MainActivity.kt"
HTML = ROOT / "app/src/main/assets/index.html"

KOTLIN = r'''package com.spidernet.accounting

import android.net.Uri
import android.os.Bundle
import android.webkit.JavascriptInterface
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.activity.ComponentActivity
import androidx.activity.OnBackPressedCallback
import androidx.activity.result.contract.ActivityResultContracts
import androidx.webkit.WebViewAssetLoader
import org.json.JSONObject

class MainActivity : ComponentActivity() {
    private lateinit var webView: WebView
    private var pendingBackupJson: String? = null

    private val createBackupDocument = registerForActivityResult(
        ActivityResultContracts.CreateDocument("application/json")
    ) { uri: Uri? ->
        val json = pendingBackupJson
        pendingBackupJson = null
        if (uri == null || json == null) {
            notifyJs("onNativeBackupResult", false, "تم إلغاء حفظ النسخة الاحتياطية")
            return@registerForActivityResult
        }
        try {
            contentResolver.openOutputStream(uri, "wt")?.bufferedWriter(Charsets.UTF_8)?.use {
                it.write(json)
                it.flush()
            } ?: throw IllegalStateException("تعذر فتح ملف الحفظ")
            notifyJs("onNativeBackupResult", true, "تم حفظ النسخة الاحتياطية بنجاح في المكان الذي اخترته")
        } catch (e: Exception) {
            notifyJs("onNativeBackupResult", false, "تعذر حفظ النسخة الاحتياطية: " + (e.message ?: "خطأ في الملف"))
        }
    }

    private val openBackupDocument = registerForActivityResult(
        ActivityResultContracts.OpenDocument()
    ) { uri: Uri? ->
        if (uri == null) {
            notifyJs("onNativeBackupLoadError", "تم إلغاء اختيار ملف الاستعادة")
            return@registerForActivityResult
        }
        try {
            val bytes = contentResolver.openInputStream(uri)?.use { input ->
                val out = java.io.ByteArrayOutputStream()
                val buffer = ByteArray(8192)
                var total = 0
                while (true) {
                    val count = input.read(buffer)
                    if (count < 0) break
                    total += count
                    if (total > MAX_BACKUP_BYTES) throw IllegalArgumentException("حجم ملف النسخة أكبر من 20 ميجابايت")
                    out.write(buffer, 0, count)
                }
                out.toByteArray()
            } ?: throw IllegalStateException("تعذر قراءة الملف المختار")
            val json = bytes.toString(Charsets.UTF_8)
            val quotedJson = JSONObject.quote(json)
            val quotedName = JSONObject.quote(uri.lastPathSegment ?: "backup.json")
            webView.post {
                webView.evaluateJavascript(
                    "window.onNativeBackupLoaded && window.onNativeBackupLoaded(" + quotedJson + ", " + quotedName + ")",
                    null
                )
            }
        } catch (e: Exception) {
            notifyJs("onNativeBackupLoadError", "تعذرت قراءة النسخة الاحتياطية: " + (e.message ?: "ملف غير صالح"))
        }
    }

    inner class BackupBridge {
        @JavascriptInterface
        fun saveBackup(json: String, fileName: String) {
            runOnUiThread {
                if (json.toByteArray(Charsets.UTF_8).size > MAX_BACKUP_BYTES) {
                    notifyJs("onNativeBackupResult", false, "حجم النسخة أكبر من 20 ميجابايت")
                    return@runOnUiThread
                }
                pendingBackupJson = json
                createBackupDocument.launch(fileName.ifBlank { "spider-net-backup.json" })
            }
        }

        @JavascriptInterface
        fun chooseBackup() {
            runOnUiThread {
                openBackupDocument.launch(arrayOf("application/json", "text/plain", "application/octet-stream"))
            }
        }
    }

    private fun notifyJs(callback: String, success: Boolean, message: String) {
        if (!::webView.isInitialized) return
        val quotedMessage = JSONObject.quote(message)
        webView.post {
            val script = if (callback == "onNativeBackupResult") {
                "window." + callback + " && window." + callback + "(" + success + ", " + quotedMessage + ")"
            } else {
                "window." + callback + " && window." + callback + "(" + quotedMessage + ")"
            }
            webView.evaluateJavascript(script, null)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        webView = WebView(this)
        setContentView(webView)
        WebView.setWebContentsDebuggingEnabled(false)
        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true
        webView.settings.allowFileAccess = false
        webView.settings.allowContentAccess = false
        webView.settings.databaseEnabled = true
        webView.addJavascriptInterface(BackupBridge(), "AndroidBackup")

        val assetLoader = WebViewAssetLoader.Builder()
            .addPathHandler("/assets/", WebViewAssetLoader.AssetsPathHandler(this))
            .build()
        webView.webViewClient = object : WebViewClient() {
            override fun shouldInterceptRequest(
                view: WebView,
                request: WebResourceRequest
            ): WebResourceResponse? = assetLoader.shouldInterceptRequest(request.url)

            override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean {
                return request.url.host != "appassets.androidplatform.net"
            }
        }
        webView.loadUrl("https://appassets.androidplatform.net/assets/index.html")
        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                if (webView.canGoBack()) webView.goBack() else finish()
            }
        })
    }

    override fun onDestroy() {
        if (::webView.isInitialized) webView.destroy()
        super.onDestroy()
    }

    companion object {
        private const val MAX_BACKUP_BYTES = 20 * 1024 * 1024
    }
}
'''

HTML_BACKUP_FUNCTIONS = r'''function backup(){
 try{
  const now=new Date().toISOString();
  const snapshot=JSON.parse(JSON.stringify(db));
  snapshot.settings.lastBackup=now;
  snapshot.audit.unshift({id:uid(),date:dateNow(),time:new Date().toLocaleTimeString('ar-YE'),action:'تصدير نسخة احتياطية',detail:'نسخة JSON'});
  snapshot.audit=snapshot.audit.slice(0,1000);
  const json=JSON.stringify(snapshot,null,2);
  const fileName='spider-net-backup-'+dateNow()+'.json';
  if(window.AndroidBackup&&typeof window.AndroidBackup.saveBackup==='function'){
   window.AndroidBackup.saveBackup(json,fileName); return;
  }
  const blob=new Blob([json],{type:'application/json;charset=utf-8'});
  const url=URL.createObjectURL(blob);const a=document.createElement('a');
  a.href=url;a.download=fileName;a.style.display='none';document.body.appendChild(a);a.click();
  setTimeout(()=>{URL.revokeObjectURL(url);a.remove()},2000);
  db.settings.lastBackup=now;persist();addAudit('طلب تنزيل نسخة احتياطية',dateNow());
 }catch(e){alert('تعذر تجهيز النسخة الاحتياطية: '+(e&&e.message?e.message:'خطأ غير معروف'))}
}
window.onNativeBackupResult=function(ok,message){
 if(ok){db.settings.lastBackup=new Date().toISOString();addAudit('حفظ نسخة احتياطية',dateNow());persist();}
 alert(message||(ok?'تم حفظ النسخة الاحتياطية':'فشل حفظ النسخة الاحتياطية'));
};
function restore(){
 if(window.AndroidBackup&&typeof window.AndroidBackup.chooseBackup==='function'){
  window.AndroidBackup.chooseBackup();return;
 }
 $('#restoreFile').click();
}
function applyBackupText(text,fileName){
 try{
  const x=JSON.parse(text);
  const requiredArrays=['cards','pos','wallets','deliveries','payments','walletLoads','walletSales','expenses','bills','partners','partnerMoves','stockAdjustments','audit','closures'];
  if(!x||x.version!==1||!x.settings||typeof x.settings!=='object'||!requiredArrays.every(k=>Array.isArray(x[k]))||(x.consignmentSettlements!==undefined&&!Array.isArray(x.consignmentSettlements)))throw Error('format');
  if(!Array.isArray(x.consignmentSettlements))x.consignmentSettlements=[];
  if(!confirm('ستُستبدل بيانات هذا الجهاز بالنسخة المختارة. تأكد من الاحتفاظ بنسخة من البيانات الحالية. هل تريد المتابعة؟'))return false;
  db=x;addAudit('استعادة نسخة احتياطية',fileName||'نسخة JSON');persist();render();alert('تمت الاستعادة بنجاح. راجع الأرصدة واختبر سلامة البيانات.');return true;
 }catch(err){alert('تعذرت استعادة النسخة أو أن ملفها ناقص. لم تُستبدل البيانات. اختر ملف JSON كاملًا صادرًا من النظام.');return false}
}
window.onNativeBackupLoaded=function(text,fileName){applyBackupText(text,fileName||'ملف مستعاد')};
window.onNativeBackupLoadError=function(message){alert(message||'تعذر فتح ملف النسخة الاحتياطية')};'''

html = HTML.read_text(encoding="utf-8")
pattern = re.compile(r"function backup\(\)\{.*?\}\s*function restore\(\)\{.*?\}", re.S)
html, count = pattern.subn(lambda _: HTML_BACKUP_FUNCTIONS, html, count=1)
if count != 1 and "window.onNativeBackupLoaded=function" not in html:
    raise SystemExit("Could not locate backup()/restore() functions in index.html")

start = html.find("$('#restoreFile').onchange=async e=>{")
if start >= 0:
    end = html.find("$('#lockBtn').onclick=", start)
    if end < 0:
        raise SystemExit("Could not locate end of restore file handler")
    html = html[:start] + "$('#restoreFile').onchange=async e=>{let f=e.target.files?.[0];if(!f)return;try{applyBackupText(await f.text(),f.name)}catch(err){alert('تعذرت قراءة ملف النسخة الاحتياطية.')}finally{e.target.value=''}};\n" + html[end:]
elif "applyBackupText(await f.text(),f.name)" not in html:
    raise SystemExit("Could not locate restore input handler in index.html")

JAVA.write_text(KOTLIN, encoding="utf-8")
HTML.write_text(html, encoding="utf-8")
print("Applied Android SAF backup and restore support.")
