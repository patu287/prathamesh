package app.notes;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Bundle;
import android.provider.MediaStore;
import android.util.Base64;
import android.util.Log;
import android.view.KeyEvent;
import android.view.ViewGroup;
import android.webkit.ConsoleMessage;
import android.webkit.DownloadListener;
import android.webkit.JavascriptInterface;
import android.webkit.PermissionRequest;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;

/**
 * Notes — a single-Activity host for the offline web app in assets/.
 *
 * The page is served from the virtual origin https://appassets.androidplatform.net/
 * rather than file:// . Every request to that host is answered locally from the APK's
 * assets, which (a) never touches the network and (b) gives the page a real, stable
 * web origin so IndexedDB, localStorage and the Web Crypto API work — a file:// page
 * gets none of those, and its data is treated as a cache and evicted.
 *
 * Three things here exist because without them each fails SILENTLY, and a silent
 * failure in a journal app is indistinguishable from a dead button:
 *
 *   onShowFileChooser    an <input type="file"> does nothing at all when tapped
 *   onPermissionRequest  getUserMedia is refused with no prompt and no error
 *   the NotesNative bridge  <a download> is ignored for blob: URLs, so the backup
 *                        export would appear to work and write nothing
 *
 * No third-party code: everything below is framework API, so the APK is a few tens
 * of kilobytes and can be built without Gradle at all (see tools/build-apk.sh).
 */
public class MainActivity extends Activity {

    private static final String HOST = "appassets.androidplatform.net";
    private static final String PREFIX = "/assets/";
    private static final String START_URL = "https://" + HOST + PREFIX + "index.html";

    private static final int REQ_FILE_CHOOSER = 1001;
    private static final int REQ_AUDIO_PERMISSION = 2001;
    private static final int REQ_SAVE_DOCUMENT = 3002;

    /** Matches the app's paper background so there is no flash while the page boots. */
    private static final int WINDOW_BG = 0xFFF6F2E9;

    private WebView web;
    private ValueCallback<Uri[]> filePathCallback;
    private PermissionRequest pendingWebRequest;
    private Uri pendingCameraUri;
    private byte[] pendingSaveData;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        clearStaleCapture();

        web = new WebView(this);
        web.setLayoutParams(new ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
        web.setBackgroundColor(WINDOW_BG);
        web.setOverScrollMode(WebView.OVER_SCROLL_NEVER);

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);               // localStorage
        s.setDatabaseEnabled(true);                 // IndexedDB — where the journal lives
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setSupportZoom(false);
        s.setBuiltInZoomControls(false);
        s.setTextZoom(100);
        s.setAllowFileAccess(false);
        s.setAllowContentAccess(true);              // needed to read a picked image URI
        s.setCacheMode(WebSettings.LOAD_NO_CACHE);  // assets are local; never serve stale JS

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

            /** Without this, tapping Camera or Gallery does nothing at all. */
            @Override
            public boolean onShowFileChooser(WebView webView,
                                             ValueCallback<Uri[]> callback,
                                             FileChooserParams params) {
                // A pending callback must always be answered, or the page's file input
                // stays locked and every later tap is ignored too.
                if (filePathCallback != null) {
                    filePathCallback.onReceiveValue(null);
                }
                filePathCallback = callback;

                // capture="environment" on the input means "take a photo now"; without
                // it, the user is choosing something they already have.
                if (params.isCaptureEnabled() && capturePhoto()) {
                    return true;
                }
                return chooseExisting(params);
            }

            /**
             * Never called on a plain file:// page — and when it is missing, or when the
             * app has not been granted RECORD_AUDIO, getUserMedia fails with no prompt,
             * no error and no retry. So the Android permission is requested here, with
             * the web request held open until the dialog is answered honestly.
             */
            @Override
            public void onPermissionRequest(final PermissionRequest request) {
                runOnUiThread(new Runnable() {
                    @Override public void run() {
                        if (!wantsAudio(request)) {
                            request.deny();
                            return;
                        }
                        if (checkSelfPermission(android.Manifest.permission.RECORD_AUDIO)
                                == PackageManager.PERMISSION_GRANTED) {
                            request.grant(new String[]{ PermissionRequest.RESOURCE_AUDIO_CAPTURE });
                        } else {
                            pendingWebRequest = request;
                            requestPermissions(
                                    new String[]{ android.Manifest.permission.RECORD_AUDIO },
                                    REQ_AUDIO_PERMISSION);
                        }
                    }
                });
            }

            @Override
            public void onPermissionRequestCanceled(PermissionRequest request) {
                if (pendingWebRequest == request) {
                    pendingWebRequest = null;
                }
            }

            @Override
            public boolean onConsoleMessage(ConsoleMessage m) {
                // Keeps the app's own error banner and logcat in agreement, which is the
                // only way to debug a WebView you are not holding.
                Log.i("Notes", m.message() + " @ " + m.lineNumber());
                return true;
            }
        });

        /* <a download> is silently ignored in a WebView for blob: URLs. The page calls
           NotesNative.saveFile() instead; this listener only stops a stray link from
           navigating the WebView away from the app. */
        web.setDownloadListener(new DownloadListener() {
            @Override
            public void onDownloadStart(String url, String userAgent, String disposition,
                                        String mimeType, long contentLength) {
                toast("Use Settings → Download backup to export.");
            }
        });

        web.addJavascriptInterface(new NotesBridge(), "NotesNative");

        setContentView(web);

        if (savedInstanceState != null) {
            web.restoreState(savedInstanceState);
        } else {
            web.loadUrl(START_URL);
        }
    }

    private static boolean wantsAudio(PermissionRequest request) {
        for (String r : request.getResources()) {
            if (PermissionRequest.RESOURCE_AUDIO_CAPTURE.equals(r)) return true;
        }
        return false;
    }

    /* ── camera ──────────────────────────────────────────────────────────────
       The camera app is handed a content:// URI from our own provider
       (CaptureProvider), so it can write a full-resolution photo without the app
       declaring CAMERA or any storage permission — and without a FileProvider,
       which would mean depending on androidx. If anything about that fails, fall
       back to the file picker: a journal is not the place to show someone a crash
       because their phone has no camera app. */
    private boolean capturePhoto() {
        try {
            Uri uri = Uri.parse("content://" + CaptureProvider.AUTHORITY + "/" + CaptureProvider.NAME);
            Intent intent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
            intent.putExtra(MediaStore.EXTRA_OUTPUT, uri);
            intent.addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION
                    | Intent.FLAG_GRANT_READ_URI_PERMISSION);
            pendingCameraUri = uri;
            startActivityForResult(intent, REQ_FILE_CHOOSER);
            return true;
        } catch (Throwable t) {
            Log.w("Notes", "camera unavailable, falling back to the picker: " + t);
            pendingCameraUri = null;
            return false;
        }
    }

    /** Honour the page's accept attribute, so the picker opens where it should. */
    private boolean chooseExisting(WebChromeClient.FileChooserParams params) {
        try {
            Intent intent = new Intent(Intent.ACTION_GET_CONTENT);
            intent.addCategory(Intent.CATEGORY_OPENABLE);
            intent.setType(acceptedType(params));
            intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE,
                    params.getMode() == WebChromeClient.FileChooserParams.MODE_OPEN_MULTIPLE);
            startActivityForResult(Intent.createChooser(intent, "Choose a file"), REQ_FILE_CHOOSER);
        } catch (ActivityNotFoundException e) {
            filePathCallback = null;
            toast("No app available to pick a file.");
            return false;
        } catch (SecurityException e) {
            filePathCallback = null;
            toast("Not allowed to pick a file on this device.");
            return false;
        }
        return true;
    }

    private static String acceptedType(WebChromeClient.FileChooserParams params) {
        String[] accept = params.getAcceptTypes();
        if (accept != null) {
            for (String a : accept) {
                if (a == null) continue;
                String t = a.trim().toLowerCase();
                if (t.length() == 0) continue;
                if (t.startsWith("image/") || t.equals(".jpg") || t.equals(".jpeg") || t.equals(".png")) {
                    return "image/*";
                }
                if (t.startsWith("audio/") || t.equals(".webm") || t.equals(".m4a")) {
                    return "audio/*";
                }
                if (t.indexOf("zip") >= 0 || t.equals(".zip")) {
                    return "application/zip";
                }
                if (t.indexOf("json") >= 0 || t.equals(".json")) {
                    return "application/json";
                }
            }
        }
        return "*/*";
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        if (requestCode == REQ_SAVE_DOCUMENT) {
            finishSave(resultCode, data);
            return;
        }
        if (requestCode != REQ_FILE_CHOOSER || filePathCallback == null) {
            return;
        }

        Uri[] results = null;
        if (resultCode == RESULT_OK) {
            if (pendingCameraUri != null) {
                results = new Uri[]{ pendingCameraUri };
            } else if (data != null && data.getClipData() != null) {
                int n = data.getClipData().getItemCount();
                results = new Uri[n];
                for (int i = 0; i < n; i++) {
                    results[i] = data.getClipData().getItemAt(i).getUri();
                }
            } else if (data != null && data.getData() != null) {
                results = new Uri[]{ data.getData() };
            }
        }

        pendingCameraUri = null;
        filePathCallback.onReceiveValue(results);   // null tells the page "cancelled"
        filePathCallback = null;
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode != REQ_AUDIO_PERMISSION || pendingWebRequest == null) return;

        boolean granted = grantResults.length > 0
                && grantResults[0] == PackageManager.PERMISSION_GRANTED;
        try {
            if (granted) {
                pendingWebRequest.grant(new String[]{ PermissionRequest.RESOURCE_AUDIO_CAPTURE });
            } else {
                pendingWebRequest.deny();
                toast("Microphone permission is needed to record a voice note.");
            }
        } catch (Throwable ignored) {
            // the web request can be cancelled while the system dialog is up
        }
        pendingWebRequest = null;
    }

    /* ── saving a backup ─────────────────────────────────────────────────────
       The web app hands us the finished .zip as base64. The system save dialog
       decides where it goes, so no storage permission is needed on any Android
       version and the user picks the folder themselves. */
    private class NotesBridge {
        @JavascriptInterface
        public boolean available() {
            return true;
        }

        @JavascriptInterface
        public void saveFile(final String filename, final String base64) {
            try {
                pendingSaveData = Base64.decode(base64, Base64.DEFAULT);
                final String name = (filename == null || filename.length() == 0)
                        ? "notes-backup.zip" : filename;
                runOnUiThread(new Runnable() {
                    @Override public void run() {
                        try {
                            Intent intent = new Intent(Intent.ACTION_CREATE_DOCUMENT);
                            intent.addCategory(Intent.CATEGORY_OPENABLE);
                            intent.setType("application/zip");
                            intent.putExtra(Intent.EXTRA_TITLE, name);
                            startActivityForResult(intent, REQ_SAVE_DOCUMENT);
                        } catch (Throwable t) {
                            pendingSaveData = null;
                            toast("Could not open a save dialog: " + t.getMessage());
                        }
                    }
                });
            } catch (Throwable t) {
                toast("Could not prepare the backup: " + t.getMessage());
            }
        }
    }

    private void finishSave(int resultCode, Intent data) {
        byte[] bytes = pendingSaveData;
        pendingSaveData = null;
        if (resultCode != RESULT_OK || data == null || data.getData() == null || bytes == null) {
            toast("Backup not saved.");
            return;
        }
        try {
            OutputStream out = getContentResolver().openOutputStream(data.getData());
            if (out == null) throw new IOException("no output stream");
            try {
                out.write(bytes);
                out.flush();
            } finally {
                out.close();
            }
            toast("Backup saved (" + (bytes.length / 1024) + " KB).");
        } catch (Throwable t) {
            toast("Could not write the backup: " + t.getMessage());
        }
    }

    /** The one capture file is overwritten each time; drop it if the app was killed
        between a capture and the page reading it, so nothing accumulates. */
    private void clearStaleCapture() {
        try {
            File dir = new File(getFilesDir(), "captures");
            File[] files = dir.listFiles();
            if (files == null) return;
            long cutoff = System.currentTimeMillis() - 24L * 60L * 60L * 1000L;
            for (File f : files) {
                if (f.lastModified() < cutoff) f.delete();
            }
        } catch (Throwable ignored) {
        }
    }

    private void toast(final String message) {
        runOnUiThread(new Runnable() {
            @Override public void run() {
                Toast.makeText(MainActivity.this, message, Toast.LENGTH_LONG).show();
            }
        });
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
