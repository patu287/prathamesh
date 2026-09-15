package app.wardrobe;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.view.KeyEvent;
import android.view.ViewGroup;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import java.io.IOException;
import java.io.InputStream;

/**
 * My Wardrobe — a single-Activity host for the offline web app in assets/.
 *
 * The page is served from the virtual origin https://appassets.androidplatform.net/
 * rather than file:// . Every request to that host is answered locally from the APK's
 * assets, which (a) never touches the network — the app declares no permissions at
 * all — and (b) gives the page a real, stable web origin so IndexedDB and
 * localStorage keep the wardrobe and its photos across restarts and app updates.
 *
 * The WebChromeClient below is the part a plain WebView wrapper usually forgets:
 * without onShowFileChooser, an <input type="file"> does nothing at all when
 * tapped, so the camera and gallery pickers would be silently dead. Picking
 * through ACTION_GET_CONTENT needs no permission — the system grants read access
 * to the single URI the user chooses — so the app still declares none.
 */
public class MainActivity extends Activity {

    private static final String HOST = "appassets.androidplatform.net";
    private static final String PREFIX = "/assets/";
    private static final String START_URL = "https://" + HOST + PREFIX + "index.html";
    private static final int FILE_CHOOSER = 1001;

    /** Matches the Dusk theme's --bg so there is no light flash while the page boots. */
    private static final int WINDOW_BG = 0xFF131110;

    private WebView web;
    private ValueCallback<Uri[]> filePathCallback;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        web = new WebView(this);
        web.setLayoutParams(new ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
        web.setBackgroundColor(WINDOW_BG);
        web.setOverScrollMode(WebView.OVER_SCROLL_NEVER);

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);              // localStorage + IndexedDB
        s.setDatabaseEnabled(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setSupportZoom(false);
        s.setBuiltInZoomControls(false);
        s.setTextZoom(100);
        s.setAllowFileAccess(false);
        s.setAllowContentAccess(true);             // needed to read a picked image URI
        s.setCacheMode(WebSettings.LOAD_NO_CACHE); // assets are local; never cache stale JS

        web.setWebViewClient(new WebViewClient() {

            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                Uri url = request.getUrl();
                if (url != null && HOST.equals(url.getHost())) {
                    String path = url.getPath();
                    if (path != null && path.startsWith(PREFIX)) {
                        String asset = path.substring(PREFIX.length());
                        try {
                            InputStream in = getAssets().open(asset);
                            return new WebResourceResponse(mimeOf(asset), "utf-8", in);
                        } catch (IOException e) {
                            return null;
                        }
                    }
                }
                return null; // anything else simply fails: the app is offline by design
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri url = request.getUrl();
                return url == null || !HOST.equals(url.getHost());
            }
        });

        web.setWebChromeClient(new WebChromeClient() {

            /** Without this, tapping "Take a photo" or "Choose from gallery" does nothing. */
            @Override
            public boolean onShowFileChooser(WebView webView,
                                             ValueCallback<Uri[]> callback,
                                             FileChooserParams params) {
                // A pending callback must always be answered, or the web input
                // stays locked and every later tap is ignored.
                if (filePathCallback != null) {
                    filePathCallback.onReceiveValue(null);
                }
                filePathCallback = callback;

                try {
                    Intent intent = new Intent(Intent.ACTION_GET_CONTENT);
                    intent.addCategory(Intent.CATEGORY_OPENABLE);
                    intent.setType(acceptedType(params));
                    intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, params.getMode()
                            == FileChooserParams.MODE_OPEN_MULTIPLE);
                    // Wrapping in a chooser lets the user reach the camera as well
                    // as their files, which is what capture="environment" implies.
                    startActivityForResult(
                            Intent.createChooser(intent, "Choose a photo"), FILE_CHOOSER);
                } catch (Exception e) {
                    filePathCallback = null;
                    return false;
                }
                return true;
            }
        });

        setContentView(web);

        if (savedInstanceState != null) {
            web.restoreState(savedInstanceState);
        } else {
            web.loadUrl(START_URL);
        }
    }

    /** Honour the page's accept attribute, defaulting to images. */
    private static String acceptedType(FileChooserParams params) {
        String[] accept = params.getAcceptTypes();
        if (accept != null) {
            for (String a : accept) {
                if (a != null && !a.trim().isEmpty()) {
                    String t = a.trim();
                    if (t.startsWith("image/") || t.equals(".jpg") || t.equals(".jpeg") || t.equals(".png")) {
                        return "image/*";
                    }
                    if (t.startsWith("application/json") || t.equals(".json")) {
                        return "application/json";
                    }
                }
            }
        }
        return "*/*";
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode != FILE_CHOOSER || filePathCallback == null) {
            return;
        }

        Uri[] results = null;
        if (resultCode == RESULT_OK && data != null) {
            if (data.getClipData() != null) {
                int n = data.getClipData().getItemCount();
                results = new Uri[n];
                for (int i = 0; i < n; i++) {
                    results[i] = data.getClipData().getItemAt(i).getUri();
                }
            } else if (data.getData() != null) {
                results = new Uri[]{ data.getData() };
            }
        }

        filePathCallback.onReceiveValue(results);   // null tells the page "cancelled"
        filePathCallback = null;
    }

    private static String mimeOf(String name) {
        if (name.endsWith(".html")) return "text/html";
        if (name.endsWith(".js"))   return "application/javascript";
        if (name.endsWith(".css"))  return "text/css";
        if (name.endsWith(".json")) return "application/json";
        if (name.endsWith(".svg"))  return "image/svg+xml";
        if (name.endsWith(".png"))  return "image/png";
        if (name.endsWith(".jpg") || name.endsWith(".jpeg")) return "image/jpeg";
        if (name.endsWith(".webp")) return "image/webp";
        if (name.endsWith(".woff2")) return "font/woff2";
        return "application/octet-stream";
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        web.saveState(outState);
    }

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        if (keyCode == KeyEvent.KEYCODE_BACK && web.canGoBack()) {
            web.goBack();
            return true;
        }
        return super.onKeyDown(keyCode, event);
    }

    @Override
    protected void onPause() {
        super.onPause();
        web.onPause();
    }

    @Override
    protected void onResume() {
        super.onResume();
        web.onResume();
    }

    @Override
    protected void onDestroy() {
        if (web != null) {
            web.destroy();
            web = null;
        }
        super.onDestroy();
    }
}
