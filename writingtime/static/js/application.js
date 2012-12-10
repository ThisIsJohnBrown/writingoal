$(function() {
	$('input[name="start-date"]').datepicker();
	$('input[name="end-date"]').datepicker();
	$('input[name="end-date"]').live('change keyup', function() {
		var startDate = new Date($('input[name="start-date"]').val());
		var endDate = new Date($('input[name="end-date"]').val());
		var days = (endDate - startDate)/1000/60/60/24;
		if (days > 0) {
			$('input[name="num-days"]').val(days);
		}
	})
	$('input[name="num-days"]').live('change keyup', function() {
		var startDate = new Date($('input[name="start-date"]').val());
		if (startDate) {
			var d = startDate.getDate();
			var m = startDate.getMonth();
			var y = startDate.getFullYear();

			var endDate = new Date(y, m, d+parseInt($('input[name="num-days"]').val()));
			$('input[name="end-date"]').val((endDate.getMonth()+1) + '/' + endDate.getDate() + '/' + endDate.getFullYear());
		}
	});

	$('button.entry-add').live('click', function(e) {
		var goalHolder = $(this).parents('.goal-holder').data('goal');
		
		var that = $(this);
		$.ajax({
			'url': $(this).data('entryUrl'),
			'type': 'POST',
			'data': {
				'goal-id': $(this).data('goalId'),
				'num-words': $($(this).data('inputClass')).val()
			},
			'success': function(data) {
				console.log(goalHolder);
				$('.goal-holder[data-goal="' + goalHolder + '"]').html(data);
			}
		})
		
	})

	$('.submit-create-goal').live('click', function() {
		$('.create-goal').serialize()
		$.ajax({
			'url': '/goals/create/',
			'type': 'POST',
			'data': $('.create-goal').serialize(),
			'success': function(data) {
				if (data.result == 'success') {
					$('#modal-create-goal').modal('hide');
				}
			}
		})
	})

	$('.entry-list-header').live('click', function() {
		console.log($(this).siblings('.entry-list').collapse('toggle'))
	})
})