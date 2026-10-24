package sa.urtv.home;

/**
 * The words of the home screen's greeting and its weather line. No Android in here, so
 * tests/greeting_test.py runs it on tests/greeting_cases.tsv.
 */
final class GreetingText {
    static final int MORNING = 0, DAY = 1, EVENING = 2, NIGHT = 3;

    private GreetingText() { }

    /** Fajr to Dhuhr, Dhuhr to Asr, Asr to Isha, and the night from Isha to the next Fajr. Times in millis. */
    static int part(long now, long fajr, long dhuhr, long asr, long isha) {
        if (now < fajr) return NIGHT;       // still the night before
        if (now < dhuhr) return MORNING;
        if (now < asr) return DAY;
        if (now < isha) return EVENING;
        return NIGHT;
    }

    static String greeting(int part) {
        switch (part) {
            case MORNING: return "Good morning";
            case DAY: return "Good afternoon";
            case EVENING: return "Good evening";
            default: return "Good night";
        }
    }

    /** Open-Meteo's WMO weather code, as a short phrase that goes before «في المدينة». */
    static String sky(int code) {
        switch (code) {
            case 0: return "Clear sky";
            case 1: return "Mainly clear";
            case 2: return "Partly cloudy";
            case 3: return "Cloudy";
            case 45: case 48: return "Fog";
            case 51: case 53: case 55: case 56: case 57: return "Drizzle";
            case 61: case 63: case 80: case 81: return "Rain";
            case 65: case 82: return "Heavy rain";
            case 66: case 67: return "Freezing rain";
            case 71: case 73: case 75: case 77: case 85: case 86: return "Snow";
            case 95: return "Thunderstorms";
            case 96: case 99: return "Thunderstorms with hail";
            default: return "";
        }
    }

    /** PM10 or dust in µg/m³ from which the air is «غبار», and «غبار كثيف»: the page's thresholds (it overrides its condition word) */
    static final double DUST = 150, HEAVY_DUST = 400;

    /** The sky's word, or «غبار» / «غبار كثيف» when the dust level (the larger of Open-Meteo's pm10 and dust) says so. */
    static String skyWord(int code, double dust) {
        if (dust >= HEAVY_DUST) return "Heavy dust";
        if (dust >= DUST) return "Dust";
        return sky(code);
    }

    /** «سماء صافية في الرياض، ٣١°» (no «·» beside a digit: the TV's font draws it as ٠); a code we have no word for gives just «الرياض، ٣١°»; dust (0 when unknown) takes the word over. */
    static String weather(int code, double dust, String city, double temp, boolean latin) {
        String sky = skyWord(code, dust);
        String place = sky.isEmpty() ? city : sky + " in " + city;
        return place + ", " + digits(Math.round(temp) + "°", latin);
    }

    /** «الغروب ٥:٥٧ م» from "17:57". */
    static String sun(String label, String hhmm, boolean latin) {
        int colon = hhmm.indexOf(':');
        int h = Integer.parseInt(hhmm.substring(0, colon));
        String m = hhmm.substring(colon + 1, colon + 3);
        int h12 = h % 12 == 0 ? 12 : h % 12;
        return label + " " + digits(h12 + ":" + m, latin) + " " + (h < 12 ? "AM" : "PM");
    }

    /** Arabic-Indic digits (as the page's #digits=hindi), or the Latin ones left alone. */
    static String digits(String s, boolean latin) {
        return DigitsText.convert(s, latin);
    }
}
