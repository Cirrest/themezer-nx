#include "font.h"
#include <switch.h>
#include <SDL2/SDL_ttf.h>

TTF_Font *FONT_TEXT[MAX_FONT], *FONT_BTN[MAX_FONT];

int FontInit(){
    if (plInitialize(0))
        return -1;

    PlFontData font, button;

    // Localization fix: PlSharedFontType_Standard only contains the Japanese
    // glyph set, so simplified-only characters (你/么/浏/览/...) render as
    // tofu boxes. Use the Simplified Chinese shared font instead; it also
    // provides Latin letters and digits. Fall back to the extended Chinese
    // font (or the standard font) on consoles where it is unavailable.
    Result rc = plGetSharedFontByType(&font, PlSharedFontType_ChineseSimplified);
    if (R_FAILED(rc))
        rc = plGetSharedFontByType(&font, PlSharedFontType_ExtChineseSimplified);
    if (R_FAILED(rc))
        rc = plGetSharedFontByType(&font, PlSharedFontType_Standard);
    if (R_FAILED(rc) || R_FAILED(plGetSharedFontByType(&button, PlSharedFontType_NintendoExt)))
        return -1;

    int font_sizes[] = { 15, 18, 20, 23, 25, 28, 30, 33, 35, 45, 48, 60, 63, 72, 170 };

    for (int i = 0; i < MAX_FONT; i++){
        FONT_TEXT[i] = TTF_OpenFontRW(SDL_RWFromMem(font.address, font.size), 1, font_sizes[i]);
        FONT_BTN[i] = TTF_OpenFontRW(SDL_RWFromMem(button.address, button.size), 1, font_sizes[i]);
    }

    return 0;
}

void FontExit(){
    for (int i = 0; i < MAX_FONT; i++){
        TTF_CloseFont(FONT_TEXT[i]);
        TTF_CloseFont(FONT_BTN[i]);
    }

    plExit();
}