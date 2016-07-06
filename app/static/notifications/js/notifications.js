(function ($, window, document, undefined) {
  "use strict";
  
  // Create the defaults once
  var pluginName = "notifications";
  var defaults = {
    // parent selector
    parentSelector           : 'body',
    // message selectors
    messageTextSelectors     : '#message-list > div',
  };
  
  // Class Constructor
  function Notification(options) {
    this.options = $.extend({}, defaults, options);
    this.init();
  }
  
  Notification.prototype = {
    init: function(element, options) {
      this.element = element;
      // Load the messages
      this.messageTextSelectors  = $(this.options.parentSelector + ' ' + this.options.messageTextSelectors);
      this.setupSystemNotifications();
    },
    setupSystemNotifications: function() {
      this.messageTextSelectors.each(function(index, element) {
        var category = $(element).data('category'),
            text = $(element).text();
        var notification = alertify.notify(text, 'success', 0);
      });
    }
  };
  
  // A really lightweight plugin wrapper around the constructor,
  // preventing against multiple instantiations
  // $.fn[pluginName] = function (options) {
  //   return this.each(function () {
  //     if (!$.data(this, "plugin_" + pluginName)) {
  //       $.data(this, "plugin_" + pluginName, new Notification(this, options));
  //     }
  //   });
  // };

  $(function() {
    var notif = new Notification();
  });
})(jQuery, window, document);
