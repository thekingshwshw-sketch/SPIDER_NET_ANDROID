package com.spidernet.accounting

import android.content.Context
import android.net.Uri
import android.print.PrintAttributes
import android.print.PrintManager
import android.util.Base64
import android.os.Bundle
import android.webkit.JavascriptInterface
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebView
import android.webkit.WebChromeClient
import android.webkit.WebViewClient
import androidx.activity.ComponentActivity
import androidx.activity.OnBackPressedCallback
import androidx.activity.result.contract.ActivityResultContracts
import androidx.webkit.WebViewAssetLoader
import org.json.JSONObject

class MainActivity : ComponentActivity() {
    private lateinit var webView: WebView
    private var pendingBackupJson: String? = null
    private var pendingImageBase64: String? = null

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

    private val createImageDocument = registerForActivityResult(
        ActivityResultContracts.CreateDocument("image/png")
    ) { uri: Uri? ->
        val base64 = pendingImageBase64
        pendingImageBase64 = null
        if (uri == null || base64 == null) {
            notifyJs("onNativeImageResult", false, "تم إلغاء حفظ صورة الكشف")
            return@registerForActivityResult
        }
        try {
            val bytes = Base64.decode(base64, Base64.DEFAULT)
            if (bytes.isEmpty() || bytes.size > MAX_IMAGE_BYTES) {
                throw IllegalArgumentException("حجم الصورة أكبر من الحد المسموح")
            }
            contentResolver.openOutputStream(uri, "wt")?.use { output ->
                output.write(bytes)
                output.flush()
            } ?: throw IllegalStateException("تعذر فتح ملف الصورة")
            notifyJs("onNativeImageResult", true, "تم حفظ صورة الكشف في المكان الذي اخترته")
        } catch (e: Exception) {
            notifyJs("onNativeImageResult", false, "تعذر حفظ صورة الكشف: " + (e.message ?: "خطأ في الملف"))
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
        fun saveImage(base64Png: String, fileName: String) {
            runOnUiThread {
                if (base64Png.isBlank() || base64Png.length > MAX_IMAGE_BASE64_CHARS) {
                    notifyJs("onNativeImageResult", false, "الصورة فارغة أو أكبر من الحد المسموح")
                    return@runOnUiThread
                }
                pendingImageBase64 = base64Png
                createImageDocument.launch(fileName.ifBlank { "spider-net-statement.png" })
            }
        }

        @JavascriptInterface
        fun printPage(jobName: String) {
            runOnUiThread {
                try {
                    val label = jobName.trim().ifBlank { "SPIDER NET" }
                    val manager = getSystemService(Context.PRINT_SERVICE) as PrintManager
                    val job = manager.print(label, webView.createPrintDocumentAdapter(label), PrintAttributes.Builder().build())
                    val cleanup = object : Runnable {
                        var attempts = 0
                        override fun run() {
                            attempts += 1
                            if (job.isCompleted || job.isCancelled || job.isFailed || attempts >= 240) {
                                webView.evaluateJavascript("document.body.classList.remove('printing-pos')", null)
                            } else {
                                webView.postDelayed(this, 500)
                            }
                        }
                    }
                    webView.postDelayed(cleanup, 500)
                    notifyJs("onNativePrintResult", true, "تم فتح واجهة طباعة Android. أكمل أو ألغِ من نافذة النظام.")
                } catch (e: Exception) {
                    notifyJs("onNativePrintResult", false, "تعذر فتح واجهة الطباعة: " + (e.message ?: "خطأ غير معروف"))
                }
            }
        }

        @JavascriptInterface
        fun chooseBackup() {
            runOnUiThread {
                openBackupDocument.launch(arrayOf("application/json", "text/plain", "application/octet-stream"))
            }
        }
    }

    private fun notifyJs(callback: String, message: String) {
        if (!::webView.isInitialized) return
        val quotedMessage = JSONObject.quote(message)
        webView.post {
            webView.evaluateJavascript(
                "window." + callback + " && window." + callback + "(" + quotedMessage + ")",
                null
            )
        }
    }

    private fun notifyJs(callback: String, success: Boolean, message: String) {
        if (!::webView.isInitialized) return
        val quotedMessage = JSONObject.quote(message)
        webView.post {
            val script = if (callback == "onNativeBackupResult" || callback == "onNativeImageResult" || callback == "onNativePrintResult") {
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
        webView.webChromeClient = WebChromeClient()
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
                webView.evaluateJavascript(
                    "window.onAndroidBackPressed ? window.onAndroidBackPressed() : false"
                ) { handled ->
                    if (handled != "true") {
                        if (webView.canGoBack()) webView.goBack() else finish()
                    }
                }
            }
        })
    }

    override fun onDestroy() {
        if (::webView.isInitialized) webView.destroy()
        super.onDestroy()
    }

    companion object {
        private const val MAX_BACKUP_BYTES = 20 * 1024 * 1024
        private const val MAX_IMAGE_BYTES = 20 * 1024 * 1024
        private const val MAX_IMAGE_BASE64_CHARS = ((MAX_IMAGE_BYTES + 2) / 3) * 4 + 16
    }
}
