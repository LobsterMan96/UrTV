package sa.urtv.home;

/**
 * The size of the box the home screen's cards (HomeCard's WebView) are drawn in, as plain arithmetic so that
 * tests/card_box_test.py can check it without Android. Everything is in pixels; the box sits dp(48) from the RIGHT and
 * dp(84) from the top, right of the greeting and clock block and above the app title and the dock. (The English chrome
 * puts the clock on the left and the cards on the right; the Arabic original was the mirror of this.)
 */
final class CardBox {
    private CardBox() { }

    /** One card is the size it always was: 461 x 250 dp. */
    static final int ONE_W = 461, ONE_H = 250;
    static final int SIDE = 48, TOP = 84;
    /** A pair is 58.44% of the screen wide: at 1920 that is 560 + 22 + 540. */
    static final float PAIR_WIDTH = 0.5844f;
    /** The height of today's single card (250 dp of 540) as a share of the screen's. */
    static final float PAIR_HEIGHT = 0.463f;

    /**
     * @param cards     how many cards (1 to 3)
     * @param clockEnd  where the greeting and clock block ENDS, from the screen's left; 0 or less: not laid out yet
     * @param titleTop  top of the block with the app title and the dock; 0 or less: not laid out yet
     * @param dockTop   top of the dock's band, in the same coordinates
     * @param titleWide the widest title among the dock's apps
     * @return {width, height}
     */
    static int[] box(int cards, int screenW, int screenH, float density, int clockEnd, int titleTop, int dockTop, int titleWide) {
        if (cards <= 1) return new int[]{dp(ONE_W, density), dp(ONE_H, density)};
        int w = Math.round(screenW * PAIR_WIDTH), h = Math.round(screenH * PAIR_HEIGHT);
        int side = dp(SIDE, density), top = dp(TOP, density);
        // the box is anchored to the right edge: what is left over once the clock block has had its say
        if (clockEnd > 0) w = Math.min(w, screenW - clockEnd - side - dp(16, density));   // clear of the clock block
        if (titleTop > 0) {
            // down to the dock, or only to the app title when the widest title would reach into the box.
            // The title sits bottom-LEFT now, so what matters is where it ends, not where it starts.
            int titleRight = dp(48, density) + dp(8, density) + titleWide;
            int boxLeft = screenW - side - w;
            int limit = titleRight <= boxLeft - dp(16, density) ? dockTop - dp(8, density) : titleTop - dp(6, density);
            h = limit - top;
        }
        return new int[]{Math.max(w, dp(300, density)), Math.max(h, dp(150, density))};
    }

    private static int dp(int v, float density) { return Math.round(v * density); }
}
