
/* Dragbetter */
!function(e){"use strict";e.event.special.dragbetterenter={setup:function(){var t=this,r=e(t);t.dragbetterCollection=[],r.on("dragenter.dragbetterenter",function(e){0===t.dragbetterCollection.length&&r.triggerHandler("dragbetterenter"),t.dragbetterCollection.push(e.target)}),r.on("drop.dragbetterenter dragend.dragbetterenter",function(){t.dragbetterCollection=[],r.triggerHandler("dragbetterleave")})},teardown:function(){e(this).off(".dragbetterenter")}},e.event.special.dragbetterleave={setup:function(){if(!this.dragbetterCollection)throw"Triggered dragbetterleave without dragbetterenter. Do you listen to dragbetterenter?";var t=this,r=e(t);r.on("dragleave.dragbetterleave",function(e){setTimeout(function(){var n=t.dragbetterCollection.indexOf(e.target);n>-1&&t.dragbetterCollection.splice(n,1),0===t.dragbetterCollection.length&&r.triggerHandler("dragbetterleave")},1)})},teardown:function(){e(this).off(".dragbetterleave")}}}(window.jQuery);

/* Reloader */
function softReload() {
	window.location = window.location.href.replace(/#.*$/, "");
}
function softRedirect(url) {
	window.location = url;
}

/* Uploader */
$(document).ready(function() {
	// Variable
	var PENDING_FILES 	= [];
	var FilePicker 		= $("#uploader-file-picker");
	var Dropbox 		= $("#uploader-dropbox");
	var UploadBtn 		= $("#uploader-submit");
	var ProgressBox		= $("#uploader-progress");
	var ProgressBar 	= $("#uploader-progress-bar");
	var InputForm		= $("#uploader-form :input");
	var UploaderForm 	= $("#uploader-form");
	var Locale 			= {
							WelcomeMsg: "<i>Drag and Drop</i> berkas anda, atau klik disini.",
							ErrorUpload: "Terjadi kesalahan saat proses unggah",
							WaitUpload: "berkas siap di unggah",
							MaxSizeLimit: "Ukuran berkas melebihi batas maksimal"
						}

	/* If uploader */
	if (UploaderForm.length) {
		bindUploader();
	}

	/* Function */
	function bindUploader() {
		// Set up the drag/drop zone.
		initDropbox();

		// Set up the handler for the file input box.
		FilePicker.on("change", function() {
			handleFiles(this.files);
			Dropbox.text(PENDING_FILES.length + " " + Locale.WaitUpload);
		});

		// Setup welcome 
		Dropbox.html(Locale.WelcomeMsg);

		// Handle the submit button.
		UploadBtn.on("click", function(e) {
			// If the user has JS disabled, none of this code is running but the
			// file multi-upload input box should still work. In this case they'll
			// just POST to the upload endpoint directly. However, with JS we'll do
			// the POST using ajax and then redirect them ourself when done.
			e.preventDefault();
			if (checkSize() && PENDING_FILES.length > 0) {
				doUpload();
			}
		});

		// Handle dropbox click
		Dropbox.click(function() {
			FilePicker.click();
		});
	}

	function checkSize() {
		if (MAX_UPLOAD_FILE_SIZE === null) {
			return true;
		}
		MaxSize		= parseInt(MAX_UPLOAD_FILE_SIZE)
		TotalSize 	= 0;
		for (var i = 0, ie = PENDING_FILES.length; i < ie; i++) {
			TotalSize += PENDING_FILES[i].size;
		}
		if (TotalSize >= MaxSize) {
			resetUpload();
			alert(Locale.MaxSizeLimit);
			return false;
		}
		return true;
	}

	function doUpload() {
		// Disable button
		UploadBtn.attr('disabled', 'disabled');
		UploadBtn.addClass('disabled');

		// Show Progressbar
		ProgressBox.slideDown('fast');

		// Initialize the progress bar.
		ProgressBar.css({"width": "0%"});

		// Collect the form data.
		FD = collectFormData();

		// Attach the files.
		for (var i = 0, ie = PENDING_FILES.length; i < ie; i++) {
			// Collect the other form data.
			FD.append("file[]", PENDING_FILES[i]);
		}

		// Inform the back-end that we're doing this over ajax.
		//FD.append("__ajax", "true");

		var xhr = $.ajax({
			xhr: function() {
				var xhrobj = $.ajaxSettings.xhr();
				if (xhrobj.upload) {
					xhrobj.upload.addEventListener("progress", function(event) {
						var percent = 0;
						var position = event.loaded || event.position;
						var total    = event.total;
						if (event.lengthComputable) {
							percent = Math.ceil(position / total * 100);
						}

						// Set the progress bar.
						ProgressBar.css({"width": percent + "%"});
						ProgressBar.text(percent + "%");
					}, false)
				}
				return xhrobj;
			},
			url: UPLOAD_URL,
			method: "POST",
			contentType: false,
			processData: false,
			cache: false,
			data: FD,
			success: function(data) {
				ProgressBar.css({"width": "100%"});
				// data = JSON.parse(data);
				// How'd it go?
				if (data == "ok") {
					softRedirect(REDIRECT_URL);
				}
				else {
					window.alert(data);
				}
				console.log(data);
				UploadBtn.removeAttr('disabled');
				UploadBtn.removeClass('disabled');
			},
			error: function (xhr, ajaxOptions, thrownError) {
				console.log(xhr.responseText);
				console.log(thrownError);
				UploadBtn.removeAttr('disabled');
				UploadBtn.removeClass('disabled');
				alert(Locale.ErrorUpload);
			}
		});
	}

	function resetUpload() {
		PENDING_FILES = [];
		Dropbox.html(Locale.WelcomeMsg);
	}

	function collectFormData() {
		// Go through all the form fields and collect their names/values.
		var FD = new FormData();

		InputForm.each(function() {
			var $this = $(this);
			var name  = $this.attr("name");
			var type  = $this.attr("type") || "";
			var value = $this.val();

			// No name = no care.
			if (name === undefined) {
				return;
			}

			// Skip the file upload box for now.
			if (type === "file") {
				return;
			}

			// Checkboxes? Only add their value if they're checked.
			if (type === "checkbox" || type === "radio") {
				if (!$this.is(":checked")) {
					return;
				}
			}

			FD.append(name, value);
		});

		return FD;
	}

	function handleFiles(files) {
		// Add them to the pending files list.
		for (var i = 0, ie = files.length; i < ie; i++) {
			PENDING_FILES.push(files[i]);
		}
	}

	function initDropbox() {
		var enteredElements = $();

		// On drag enter...
		Dropbox.on("dragbetterenter", function(e) {
			e.stopPropagation();
			e.preventDefault();
			$(this).addClass("active");
		});

		// On drag over...
		Dropbox.on("dragover", function(e) {
			e.stopPropagation();
			e.preventDefault();
		});

		// On drag leave...
		Dropbox.on("dragbetterleave", function(e) {
			e.stopPropagation();
			e.preventDefault();
			$(this).removeClass("active");
		});

		// On drop...
		Dropbox.on("drop", function(e) {
			e.preventDefault();
			$(this).removeClass("active");

			// Get the files.
			var files = e.originalEvent.dataTransfer.files;
			handleFiles(files);

			// Update the display to acknowledge the number of pending files.
			Dropbox.text(PENDING_FILES.length + " " + Locale.WaitUpload);
		});

		// If the files are dropped outside of the drop zone, the browser will
		// redirect to show the files in the window. To avoid that we can prevent
		// the 'drop' event on the document.
		function stopDefault(e) {
			e.stopPropagation();
			e.preventDefault();
		}
		$(document).on("dragbetterenter", stopDefault);
		$(document).on("dragover", stopDefault);
		$(document).on("dragbetterleave", stopDefault);
		$(document).on("drop", stopDefault);
	}
});