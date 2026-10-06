package app.notes;

import android.content.ContentProvider;
import android.content.ContentValues;
import android.database.Cursor;
import android.net.Uri;
import android.os.ParcelFileDescriptor;

import java.io.File;
import java.io.FileNotFoundException;

/**
 * The photo hand-off between the camera app and this one.
 *
 * A full-resolution capture needs somewhere for the camera to write, and the
 * obvious answers are both wrong here:
 *
 *   file:// URI         throws FileUriExposedException on API 24+ — you may not
 *                       hand a file path to another app
 *   androidx FileProvider  exactly this, but it is a Maven dependency, and this
 *                       app is deliberately buildable with no dependency
 *                       resolution at all (see tools/build-apk.sh)
 *   ACTION_IMAGE_CAPTURE without EXTRA_OUTPUT
 *                       returns only a thumbnail in the result extras — far too
 *                       small to be worth keeping in a journal
 *   MediaStore insert   works, but on API 24–28 it needs WRITE_EXTERNAL_STORAGE,
 *                       and this app declares no storage permission
 *
 * So: a ContentProvider of our own, serving one file inside the app's private
 * storage. The camera app gets a temporary write grant for the duration of the
 * capture intent and nothing more; the page reads the same URI back a moment
 * later through the file chooser. The file is a single fixed name, overwritten
 * on every capture, so it cannot grow.
 */
public class CaptureProvider extends ContentProvider {

    public static final String AUTHORITY = "app.notes.capture";
    public static final String NAME = "capture.jpg";

    private File target() {
        File dir = new File(getContext().getFilesDir(), "captures");
        if (!dir.exists()) dir.mkdirs();
        return new File(dir, NAME);
    }

    @Override
    public boolean onCreate() {
        return true;
    }

    /**
     * The mode handling is the whole point of this class. Opening for read must
     * NOT truncate: the page reads this file back through the same URI after the
     * camera has written it, and a provider that always passed MODE_TRUNCATE
     * would hand the page a zero-byte photo — a silent data loss with no error
     * anywhere, which is exactly the class of bug this app tries never to have.
     */
    @Override
    public ParcelFileDescriptor openFile(Uri uri, String mode) throws FileNotFoundException {
        int flags;
        if ("r".equals(mode)) {
            flags = ParcelFileDescriptor.MODE_READ_ONLY;
        } else if ("w".equals(mode) || "wt".equals(mode)) {
            flags = ParcelFileDescriptor.MODE_WRITE_ONLY
                    | ParcelFileDescriptor.MODE_CREATE
                    | ParcelFileDescriptor.MODE_TRUNCATE;
        } else if ("wa".equals(mode)) {
            flags = ParcelFileDescriptor.MODE_WRITE_ONLY
                    | ParcelFileDescriptor.MODE_CREATE
                    | ParcelFileDescriptor.MODE_APPEND;
        } else if ("rw".equals(mode)) {
            flags = ParcelFileDescriptor.MODE_READ_WRITE | ParcelFileDescriptor.MODE_CREATE;
        } else if ("rwt".equals(mode)) {
            flags = ParcelFileDescriptor.MODE_READ_WRITE
                    | ParcelFileDescriptor.MODE_CREATE
                    | ParcelFileDescriptor.MODE_TRUNCATE;
        } else {
            throw new FileNotFoundException("Unsupported mode: " + mode);
        }
        return ParcelFileDescriptor.open(target(), flags);
    }

    @Override
    public String getType(Uri uri) {
        return "image/jpeg";
    }

    /* ── the parts of ContentProvider that this provider does not use ──────── */

    @Override
    public Cursor query(Uri uri, String[] projection, String selection,
                        String[] selectionArgs, String sortOrder) {
        return null;
    }

    @Override
    public Uri insert(Uri uri, ContentValues values) {
        return null;
    }

    @Override
    public int delete(Uri uri, String selection, String[] selectionArgs) {
        return 0;
    }

    @Override
    public int update(Uri uri, ContentValues values, String selection, String[] selectionArgs) {
        return 0;
    }
}
