(function($){  //$-safe plugin

var AttachedImagesAdminUploader = new Class({
    Extends: DjangoImageUploader,

    options: {
        formsetPrefix: 'generic_images-attachedimage-content_type-object_id',
        user: '',
        previewWidth: 200
    },

    isFormsetField: function(name){
        var pref = this.options.formsetPrefix;
        return name.substring(0, pref.length) == pref;
    },

    cleanupFields: function(fields){
        var cleanedFields = {};
        var self = this;
        var denied_names = ['_save', '_addanother', '_continue'];
        $each(fields, function(value, name){
            if (name && !(name in denied_names) && !self.isFormsetField(name))
                cleanedFields[name]=value;
        });
        return cleanedFields;
    },

    getNewFormsetFields: function(){
        var fields = {};
        var prefix = this.options.formsetPrefix+'-';
        for (var i = 0; i < this.files.length; i++) {
            fields[prefix + i + '-id'] = '';
            fields[prefix + i + '-caption'] = '';
            fields[prefix + i + '-order'] = '0';
            fields[prefix + i + '-user'] = this.options.user;
        }
        return fields;
    },

    getFormFields: function(){
        if (this.options.formElement == null)
            this.options.formElement = $$('form')[0];

        var existing = this.cleanupFields(this.getExistingFormFields());
        var management = this.getManagementFields();
        var generated = this.getNewFormsetFields();

        return $merge(existing, management, generated);
    }

});

window.addEvent('domready', function(){

    if (!window.google || !google.gears)
        return;

    if (google.gears.factory.version < '0.5.21')
        return;

    if ($('gears-uploader'))
    {
        var pb = new ProgressBar({
            container:'progress-bar',
            displayText: true,
            speed: 100
        });

        function getMaxWidth()
        {
            if ($('gears-resize-needed').checked)
                return $('gears-resize-width').value;
            return null;
        }

        var uploader = new AttachedImagesAdminUploader({
            statusElement: 'upload-status',
            previewsElement: 'thumbs',
            fileElementName: 'image',
            progressBar: pb,
            user: $('request-user-id').get('text'),
            maxWidth: getMaxWidth(),

            onUploadComplete: function(){
                setTimeout(function(){window.location.reload();},0);
            },
            onBeforeProcess: function(){
                this.options.maxWidth = getMaxWidth();
            }
        });

        $('gears-uploader').show();
        $('gears-please-install').hide();
    }
});

})(document.id); // end $-safe plugin
