/**
 * Error Blocker
 * This script completely blocks WebGL errors from appearing in the console
 * It must be loaded before any other scripts
 */
(function() {
    // Store original console methods
    const originalConsole = {
        error: console.error,
        warn: console.warn,
        log: console.log,
        debug: console.debug,
        info: console.info
    };
    
    // Function to check if a message is WebGL related
    function isWebGLRelated(msg) {
        if (typeof msg !== 'string') return false;
        
        const webglTerms = [
            'WebGL', 'GL_', 'gl_utils', 'gl_surface', 'GetVSyncParametersIfAvailable',
            'Texture format', 'mipmap', 'INVALID_OPERATION', 'glTexImage', 'glGenerate'
        ];
        
        return webglTerms.some(term => msg.includes(term));
    }
    
    // Replace console methods
    console.error = function(...args) {
        if (args.length > 0 && isWebGLRelated(args[0])) {
            // Silently drop WebGL errors
            return;
        }
        return originalConsole.error.apply(console, args);
    };
    
    console.warn = function(...args) {
        if (args.length > 0 && isWebGLRelated(args[0])) {
            // Silently drop WebGL warnings
            return;
        }
        return originalConsole.warn.apply(console, args);
    };
    
    // Create a more aggressive error handler by overriding the Error constructor
    const originalErrorConstructor = window.Error;
    window.Error = function(message) {
        if (isWebGLRelated(message)) {
            // For WebGL errors, return a dummy error that won't be reported
            return {
                message: "[Suppressed WebGL Error]",
                toString: () => "[Suppressed WebGL Error]",
                stack: ""
            };
        }
        return new originalErrorConstructor(message);
    };
    
    // Preserve the prototype chain
    window.Error.prototype = originalErrorConstructor.prototype;
    
    // Block error events
    window.addEventListener('error', function(event) {
        if (event && event.message && isWebGLRelated(event.message)) {
            event.preventDefault();
            event.stopPropagation();
            return false;
        }
    }, true);
    
    // Block unhandled rejection events
    window.addEventListener('unhandledrejection', function(event) {
        if (event && event.reason && event.reason.message && isWebGLRelated(event.reason.message)) {
            event.preventDefault();
            event.stopPropagation();
            return false;
        }
    }, true);
    
    // Notify that the error blocker is loaded
    originalConsole.log('Error Blocker loaded - WebGL errors will be suppressed');
})();
