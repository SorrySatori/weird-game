/**
 * LanguageSystem.js — Internationalization system for Upper Morkezela
 * 
 * Provides key-based translation for UI strings and text-matching translation
 * for dialog content (intercepted in GameScene.showDialog).
 * 
 * Supported languages: 'en' (English, default), 'cs' (Czech)
 */

import en from '../lang/en/index.js';
import cs from '../lang/cs/index.js';

let instance = null;

export default class LanguageSystem {
    constructor() {
        if (instance) return instance;
        
        this.languages = { en, cs };
        this.supportedLanguages = [
            { code: 'en', name: 'English' },
            { code: 'cs', name: 'Čeština' },
        ];
        
        // Load saved preference or default to English
        this.currentLanguage = 'en';
        try {
            const saved = localStorage.getItem('gameLanguage');
            if (saved && this.languages[saved]) {
                this.currentLanguage = saved;
            }
        } catch (e) {
            // localStorage not available, keep default
        }
        
        instance = this;
    }

    static getInstance() {
        if (!instance) {
            instance = new LanguageSystem();
        }
        return instance;
    }

    /**
     * Get the current language code
     */
    getLanguage() {
        return this.currentLanguage;
    }

    /**
     * Set language and persist preference
     */
    setLanguage(langCode) {
        if (!this.languages[langCode]) return;
        this.currentLanguage = langCode;
        try {
            localStorage.setItem('gameLanguage', langCode);
        } catch (e) {
            // localStorage not available
        }
    }

    /**
     * Key-based translation lookup.
     * Keys use dot notation: 'ui.menu.startGame', 'notifications.questUpdated'
     * Supports parameter interpolation: t('ui.gold', { amount: 50 }) → '+50 gold'
     */
    t(key, params = {}) {
        const lang = this.languages[this.currentLanguage];
        if (!lang) return key;
        
        let value = this._resolve(lang, key);
        
        // Fall back to English if key not found in current language
        if (value === undefined && this.currentLanguage !== 'en') {
            value = this._resolve(this.languages.en, key);
        }
        
        if (value === undefined) return key;
        
        // For non-string values (arrays, objects), return directly without interpolation
        if (typeof value !== 'string') return value;
        
        return this._interpolate(value, params);
    }

    /**
     * Translate dialog content for a scene.
     * Returns translated content object or null if no translation available.
     * Used by GameScene.showDialog() interceptor.
     */
    translateDialog(sceneKey, dialogState, content) {
        if (this.currentLanguage === 'en') return content;
        
        const lang = this.languages[this.currentLanguage];
        if (!lang?.dialogs?.[sceneKey]) return content;
        
        const sceneDialogs = lang.dialogs[sceneKey];
        const stateTrans = sceneDialogs[dialogState];
        
        // Clone content to avoid mutating original
        const translated = { ...content };
        
        // Translate speaker name
        if (translated.speaker && sceneDialogs._speakers?.[translated.speaker]) {
            translated.speaker = sceneDialogs._speakers[translated.speaker];
        }
        
        // Translate main text
        if (stateTrans?.text) {
            if (typeof stateTrans.text === 'string') {
                // Single translation — always replace
                translated.text = stateTrans.text;
            } else if (typeof stateTrans.text === 'object' && translated.text) {
                // Key-based lookup (textKey on content) or fallback to text matching
                const variant = translated.textKey || translated.text;
                const czechText = stateTrans.text[variant];
                if (czechText) {
                    translated.text = czechText;
                }
            }
        }
        
        // Translate options — use opt.key for lookup, fallback to opt.text
        if (stateTrans?.options && translated.options) {
            translated.options = translated.options.map(opt => {
                const lookupKey = opt.key || opt.text;
                const translatedText = stateTrans.options[lookupKey];
                return translatedText ? { ...opt, text: translatedText } : opt;
            });
        }
        
        return translated;
    }

    /**
     * Resolve a dot-notation key in an object
     */
    _resolve(obj, path) {
        return path.split('.').reduce((acc, key) => acc?.[key], obj);
    }

    /**
     * Replace {param} placeholders with values
     */
    _interpolate(text, params) {
        if (!params || Object.keys(params).length === 0) return text;
        return text.replace(/\{(\w+)\}/g, (_, key) => 
            params[key] !== undefined ? params[key] : `{${key}}`
        );
    }
}
