$(document).ready(function() {
	$('.select-all').click(function() {
		console.log();
		newState = this.checked;
		$($(this).attr('selection')).each( function() {
			this.checked = newState;
		});
	});
	$('.tag-select-set').select2({
		placeholder: 'choose tags',
		tags: true
	});
	$('.tag-search').click(function() {
		if ($('.tag-select').val() === null) {
			window.location = '/';
		} else {
			tagStr = $('.tag-select').val().join(',');
			window.location = '/problems/tags/' + tagStr;
		}
	});

	$('.tr-link').click(function() {
		window.location = $(this).data('href');
	});
});
