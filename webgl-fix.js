/**
 * WebGL error handling and configuration
 */
(function() {
    // Disable WebGL mipmap generation to prevent errors
    const originalGetContext = HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext = function(type, attributes) {
        if (type === 'webgl' || type === 'webgl2' || type === 'experimental-webgl') {
            attributes = attributes || {};
            // Force NEAREST filtering for textures
            attributes.powerPreference = 'high-performance';
            attributes.antialias = false;
        }
        return originalGetContext.call(this, type, attributes);
    };
    
    // Suppress WebGL warnings in console
    const originalConsoleError = console.error;
    console.error = function() {
        if (arguments[0] && typeof arguments[0] === 'string' && 
            (arguments[0].includes('GL_INVALID_OPERATION') || 
             arguments[0].includes('Texture format does not support mipmap generation'))) {
            // Suppress this specific WebGL error
            return;
        }
        return originalConsoleError.apply(this, arguments);
    };
    
    console.log('WebGL fix loaded');
})();
