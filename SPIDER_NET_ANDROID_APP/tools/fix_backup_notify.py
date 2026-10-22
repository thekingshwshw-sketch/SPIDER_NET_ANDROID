from pathlib import Path

p = Path(__file__).resolve().parents[1] / "app/src/main/java/com/spidernet/accounting/MainActivity.kt"
s = p.read_text(encoding="utf-8")
needle = '    private fun notifyJs(callback: String, success: Boolean, message: String) {'
overload = '''    private fun notifyJs(callback: String, message: String) {
        if (!::webView.isInitialized) return
        val quotedMessage = JSONObject.quote(message)
        webView.post {
            webView.evaluateJavascript(
                "window." + callback + " && window." + callback + "(" + quotedMessage + ")",
                null
            )
        }
    }

'''
if "private fun notifyJs(callback: String, message: String)" not in s:
    if needle not in s:
        raise SystemExit("Expected notifyJs function not found; refusing to patch silently")
    s = s.replace(needle, overload + needle, 1)
    p.write_text(s, encoding="utf-8")
print("Fixed JavaScript callback overload for restore errors.")
