$(function() {
	$('form input[name="tz"]').val(new Date().getTimezoneOffset());
	$('*[rel="tooltip"]').tooltip();

	$('input[name="start-date"]').datepicker();
	$('input[name="end-date"]').datepicker();
	$('input[name="end-date"]').live('change keyup', function() {
		var startDate = new Date($(this).siblings('input[name="start-date"]').val());
		var endDate = new Date($(this).val());
		var days = (endDate - startDate)/1000/60/60/24;
		if (days > 0) {
			$(this).siblings('input[name="num-days"]').val(days);
		}
	})
	$('input[name="num-days"]').live('change keyup', function() {
		var startDate = new Date($(this).siblings('input[name="start-date"]').val());
		if (startDate) {
			var d = startDate.getDate();
			var m = startDate.getMonth();
			var y = startDate.getFullYear();

			var endDate = new Date(y, m, d+parseInt($(this).val()));
			$(this).siblings('input[name="end-date"]').val((endDate.getMonth()+1) + '/' + endDate.getDate() + '/' + endDate.getFullYear());
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
				'num-words': $($(this).data('inputClass')).val(),
				'tz': Math.round(new Date().getTime()/1000) - (new Date().getTimezoneOffset()*60)
			},
			'success': function(data) {
				updateGoal(goalHolder, data);
			}
		})
		
	})

	$('.submit-create-goal').live('click', function(e) {
		e.preventDefault();
		$.ajax({
			'url': $('.create-goal').attr('action'),
			'type': 'POST',
			'data': $('.create-goal').serialize(),
			'success': function(data) {
				$('#modal-create-goal').modal('hide');
				$('.goals').prepend('<div class="goal-holder"></div>')
				$('.goals .goal-holder:eq(0)').html(data);
			}
		})
	})

	$('.submit-update-goal').live('click', function(e) {
		e.preventDefault();
		$.ajax({
			'url': $('.update-goal').attr('action'),
			'type': 'POST',
			'data': $('.update-goal').serialize(),
			'success': function(data) {
				$('#modal-update-goal').modal('hide');
				updateGoal($('.update-goal input[name="goal-id"]').val(), data);
			}
		})
	})

	$('.submit-delete-goal').live('click', function(e) {
		e.preventDefault();
		var that = $(this);
		$.ajax({
			'url': '/goals/delete/',
			'type': 'POST',
			'data': {
				'goal-id': $(this).data('id')
			},
			'success': function(data) {
				$('#modal-delete-goal').modal('hide');
				$('.goal-holder[data-goal="' + that.data('id') + '"]').remove()
			}
		})
	})

	$('.entry-list-header').live('click', function() {
		$(this).siblings('.entry-list').collapse('toggle');
		$(this).toggleClass('expanded');
	})
	$('.entry-list-day-header').live('click', function() {
		$($(this).data('collapseName')).collapse('toggle');
		$(this).toggleClass('expanded');
	})
	$('body').live('click', function(e) {
		var editing = $(e.target).parents('.editing');
		$('.editing').each(function() {
			if ($(this).data('entryId') != editing.data('entryId')) {
				dayToggle($(this));
			}
		})
	})

	function updateGoal(goalHolder, html) {
		var a = $('.goal-holder[data-goal="' + goalHolder + '"]').find('.collapse.in');
		var classes = [];
		a.each(function() {
			classes.push('.' + $(this).removeClass('in').attr('class').replace(/ /g, '.'));
		})
		$('.goal-holder[data-goal="' + goalHolder + '"]').html(html);
		for (clas in classes) {
			$('.goal-holder[data-goal="' + goalHolder + '"]').find(classes[clas]).addClass('in')
		}
	}

	function dayToggle(day) {
		var start = day.find('.start-icons');
		var edit = day.find('.edit-icons');

		var words = day.find('.words');
		var input = words.find('input');
		var span = words.find('span');

		day.toggleClass('editing');
		start.toggleClass('hidden');
		edit.toggleClass('hidden');
		input.toggleClass('hidden');
		span.toggleClass('hidden');
	}

	$('.delete-goal').live('click', function(e) {
		var modal = $($(this).attr('href'));
		var data = $(this).data();
		modal.find('.submit-delete-goal').data('id', data['id']);
	})

	$('.update-goal').live('click', function(e) {
		var modal = $($(this).attr('href'));
		var data = $(this).data();
		modal.find('input[name="goal-name"]').val(data['name']);
		modal.find('input[name="num-words"]').val(data['words']);
		modal.find('input[name="start-date"]').val(data['start']);
		modal.find('input[name="end-date"]').val(data['end']);
		modal.find('input[name="num-days"]').val(data['days']);
		modal.find('input[name="goal-id"]').val(data['id']);
	})

	$('.edit-word-count').live('click', function(e) {
		e.preventDefault();

		var day = $(this).parents('.day');
		var words = day.find('.words');
		var input = words.find('input');
		var span = words.find('span');

		if (input.hasClass('hidden')) {
			input.val(span.text());
		} else {
			span.text(input.val());
		}

		dayToggle(day);
	});

	$('.cancel-entry-update').live('click', function(e) {
		e.preventDefault();
		dayToggle($(this).parents('.day'));
	})

	$('.update-entry').live('click', function(e) {
		e.preventDefault();
		var goalHolder = $(this).parents('.goal-holder').data('goal');
		var day = $(this).parents('.day');
		var words = day.find('.words');
		var input = words.find('input');

		$.ajax({
			'url': '/goals/entry/update/',
			'type': 'POST',
			'data': {
				'entry-id': day.data('entryId'),
				'num-words': input.val()
			},
			'success': function(data) {
				updateGoal(goalHolder, data);
			}
		})
	})

	$('.delete-entry').live('click', function(e) {
		e.preventDefault();
		var goalHolder = $(this).parents('.goal-holder').data('goal');
		var day = $(this).parents('.day');

		$.ajax({
			'url': '/goals/entry/delete/',
			'type': 'POST',
			'data': {
				'entry-id': day.data('entryId'),
			},
			'success': function(data) {
				updateGoal(goalHolder, data);
			}
		})
	})

	$('.words input').live('keyup', function(e) {
		if (e.keyCode == 13) {
			$(this).parents('.day').find('.icon-check').click();
		}
	})

	$('.word-count').live('click', function(e) {
		$(this).parents('.day').find('.icon-edit').click();
	})
})