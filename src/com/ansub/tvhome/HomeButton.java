package com.ansub.tvhome;

import android.accessibilityservice.AccessibilityService;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageManager;
import android.content.pm.ResolveInfo;
import android.os.Build;
import android.os.SystemClock;
import android.provider.Settings;
import android.view.accessibility.AccessibilityEvent;

// Opt-in (Settings > Accessibility > Home button): makes Home open this home screen on TVs where the
// TV's own home screen has to stay on, like Google TV and Chromecast. Nothing gets turned off, so
// switching it off puts Home straight back to the TV's own.
//
// Google TV handles the Home key before accessibility services see it, so this doesn't watch keys.
// It watches for the stock home screen to open, after Home or a restart, and opens this one over it.
// It knows all three stock launchers: Google TV's (launcherx), Android TV 9-11's (tvlauncher) and
// the older leanback launcher. Only each package's own HOME activity is watched, so Google TV's
// other pages (Apps, Settings) are left alone.
public class HomeButton extends AccessibilityService {
    // Stock home screen packages, newest first. THE SAME ORDER as KNOWN_HOME below.
    private static final String[] STOCK_PACKAGES = {
            "com.google.android.apps.tv.launcherx",
            "com.google.android.tvlauncher",
            "com.google.android.leanbacklauncher"};
    // Fallbacks for when the package manager can't resolve a package's HOME activity.
    private static final String[] KNOWN_HOME = {
            "com.google.android.apps.tv.launcherx.home.HomeActivity",
            "com.google.android.tvlauncher.MainActivity",
            "com.google.android.leanbacklauncher.MainActivity"};
    static final int HOME_ENABLED = 1, HOME_DISABLED = 2, HOME_MISSING = 0;
    // Debounce duplicate events until the activity resumes.
    private static long lastOpened = -500;

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
        if (event.getEventType() != AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED
                || !isStockHome(String.valueOf(event.getPackageName()),
                        String.valueOf(event.getClassName())) || !setupDone()) return;
        SharedPreferences prefs = prefs(this);
        if (stayingOnGoogleTv(prefs)) return;
        long now = SystemClock.elapsedRealtime();
        if (now - lastOpened < 500) return;

        // Give an unfinished launch time to resume. Successful launches don't delay the next Home.
        long pending = prefs.getLong("pending", -1);
        if (pending >= 0 && now >= pending && now - pending < 3000) return;
        int failures = prefs.getInt("failures", 0);
        if (pending >= 0) failures++;
        if (failures >= 3) {
            prefs.edit().remove("pending").putInt("failures", failures).commit();
            return;
        }
        // Save before launching: a crash can take the service down with the activity.
        if (!prefs.edit().putLong("pending", now).putInt("failures", failures).commit()) return;
        lastOpened = now;
        try {
            startActivity(new Intent(this, MainActivity.class).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));
        } catch (Exception ignored) {}
    }

    @Override
    public void onInterrupt() {}

    // During the TV's first setup, Home is left alone.
    private boolean setupDone() {
        return Settings.Secure.getInt(getContentResolver(), "user_setup_complete", 1) == 1;
    }

    private static SharedPreferences prefs(Context c) {
        return c.getSharedPreferences("home_button", 0);
    }

    // Back on this home screen: Home comes here again.
    static void onHomeResumed(Context c) {
        prefs(c).edit().remove("google_tv_boot").remove("google_tv_boot_count").commit();
    }

    // This home screen opened and didn't crash. Also resets a stopped redirect loop.
    static void onHomeOk(Context c) {
        prefs(c).edit().remove("pending").remove("failures").commit();
        lastOpened = -500;
    }

    private static int bootCount(Context c) {
        return Build.VERSION.SDK_INT >= 24
                ? Settings.Global.getInt(c.getContentResolver(), Settings.Global.BOOT_COUNT, -1) : -1;
    }

    private static long bootTime() {
        return System.currentTimeMillis() - SystemClock.elapsedRealtime();
    }

    private boolean stayingOnGoogleTv(SharedPreferences prefs) {
        if (!prefs.contains("google_tv_boot")) return false;
        int boot = bootCount(this);
        int saved = prefs.getInt("google_tv_boot_count", -1);
        if (boot >= 0 && saved >= 0) return boot == saved;
        return Math.abs(bootTime() - prefs.getLong("google_tv_boot", 0)) < 5000;
    }

    // The stock home activity installed on this TV, or null when there is none. Read-only: nothing
    // is enabled, disabled or started here.
    static ComponentName stockHome(Context c) {
        PackageManager pm = c.getPackageManager();
        for (String pkg : STOCK_PACKAGES) {
            try {
                if (!pm.getApplicationInfo(pkg, 0).enabled) continue;
            } catch (Exception e) {
                continue;
            }
            Intent i = new Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_HOME).setPackage(pkg);
            ResolveInfo ri = pm.resolveActivity(i, PackageManager.MATCH_DEFAULT_ONLY);
            if (ri != null && ri.activityInfo != null) return new ComponentName(pkg, ri.activityInfo.name);
        }
        return null;
    }

    // For the Settings row. HOME_ENABLED when a stock home can be opened, HOME_DISABLED when one is
    // installed but turned off, HOME_MISSING when this TV has none of them.
    static int stockHomeState(Context c) {
        if (stockHome(c) != null) return HOME_ENABLED;
        for (String pkg : STOCK_PACKAGES) {
            try {
                if (!c.getPackageManager().getApplicationInfo(pkg, 0).enabled) return HOME_DISABLED;
            } catch (Exception ignored) {}
        }
        return HOME_MISSING;
    }

    // True only for a stock package's own HOME activity.
    private boolean isStockHome(String pkg, String cls) {
        for (int i = 0; i < STOCK_PACKAGES.length; i++) {
            if (!STOCK_PACKAGES[i].equals(pkg)) continue;
            Intent i2 = new Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_HOME).setPackage(pkg);
            ResolveInfo ri = getPackageManager().resolveActivity(i2, PackageManager.MATCH_DEFAULT_ONLY);
            String home = ri != null && ri.activityInfo != null ? ri.activityInfo.name : KNOWN_HOME[i];
            return home.equals(cls);
        }
        return false;
    }

    // Opens the TV's own home screen and keeps it there. False if this TV doesn't have one.
    static boolean openGoogleTv(Context c) {
        ComponentName home = stockHome(c);
        if (home == null) return false;
        SharedPreferences prefs = prefs(c);
        // Keep the choice through process death and updates, but not a TV restart.
        if (!prefs.edit().putLong("google_tv_boot", bootTime())
                .putInt("google_tv_boot_count", bootCount(c)).commit()) return false;
        try {
            c.startActivity(new Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_HOME)
                    .setComponent(home).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));
            return true;
        } catch (Exception e) {
            prefs.edit().remove("google_tv_boot").remove("google_tv_boot_count").commit();
            return false;
        }
    }
}
