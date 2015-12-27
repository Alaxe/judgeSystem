$(document).ready(function() {
	$('.select-all').click(function() {
		console.log();
		newState = this.checked;
		$($(this).attr('selection')).each( function() {
			this.checked = newState;
		});
	});
	$('.tr-link').click(function() {
		window.location = $(this).data('href');
	});
});
