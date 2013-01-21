$(function() {
	$('form input[name="tz"]').val(new Date().getTimezoneOffset());
	$('*[rel="tooltip"]').tooltip();

	$('input[name="start-date"]').datepicker();
	$('input[name="end-date"]').datepicker();

	setSubgoalMarkers();
	$('.tooltip-inner').livequery(function() {
		var oW = $(this).width();
		$(this).html($(this).html().replace('&lt;br&gt;', '<br>'))
		var nW = $(this).width();
		var left = parseInt($(this).parents('.tooltip').css('left'))
		$(this).parents('.tooltip').css({'left': left + ((oW - nW)/2) + 'px'})
	});
	$(window).resize(setSubgoalMarkers);

	$('.start-now').live('click', function() {
		if ($(this).is(':checked')) {
			var date = new Date();
			$(this).siblings('input[name="start-date"]').val((date.getMonth() + 1) + '/' + date.getDate() + '/' + date.getFullYear()).prop('disabled', true);;
		} else {
			$(this).siblings('input[name="start-date"]').prop('disabled', false);;
		}
	})

	$('.open-ended').live('click', function() {
		if ($(this).is(':checked')) {
			$(this).siblings('input[name="start-date"]').prop('disabled', true).val('');
			$(this).siblings('input[name="end-date"]').prop('disabled', true).val('');
			$(this).siblings('input[name="num-days"]').prop('disabled', true).val('');
		} else {
			$(this).siblings('input[name="start-date"]').prop('disabled', false);
			$(this).siblings('input[name="end-date"]').prop('disabled', false);
			$(this).siblings('input[name="num-days"]').prop('disabled', false);
		}
	})

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

	$('.open-subgoal-modal').live('click', function(e) {
		$('#modal-create-subgoal input[name="subgoal"]').val($(this).data('goal'))
	})

	$('.submit-create-goal').live('click', function(e) {
		e.preventDefault();
		var that = this;
		$('.create-goal input[name="ts"]').val(Math.round(new Date().getTime()/1000) - (new Date().getTimezoneOffset()*60))
		var modal = $(this).parents('.modal');
		var error = errorCheckGoal(modal);
		
		if (!error) {
			
			$.ajax({
				'url': $('.create-goal').attr('action'),
				'type': 'POST',
				'data': $(this).parents('.modal').find('.create-goal').serialize(),
				'success': function(data) {
					$(that).parents('.modal').modal('hide');
					if ($(that).parents('.modal').find('input[name="subgoal"]').length) {
						console.log(data);
						console.log($(that).parents('.modal').find('input[name="subgoal"]').val());
						console.log($(that).parents('.modal').find('input[name="subgoal"]'));
						console.log('.goal-holder[data-goal="' + $(that).parents('.modal').find('input[name="subgoal"]').val() + '"]');
						console.log($('.goal-holder[data-goal="' + $(that).parents('.modal').find('input[name="subgoal"]').val() + '"]').length);
						updateGoal($(that).parents('.modal').find('input[name="subgoal"]').val(), data);
					} else {
						$('.goals').prepend('<div class="goal-holder"></div>')
						$('.goals .goal-holder:eq(0)').html(data);
					}
				}
			})
		}
		
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
		var parentId = $(this).data('parentId');
		$.ajax({
			'url': '/goals/delete/',
			'type': 'POST',
			'data': {
				'goal-id': $(this).data('id')
			},
			'success': function(data) {
				$('#modal-delete-goal').modal('hide');
				if (!parentId) {
					$('.goal-holder[data-goal="' + that.data('id') + '"]').remove()
				} else {
					console.log(parentId);
					updateGoal(parentId, data);
				}
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
		$('*[rel="tooltip"]').tooltip();
		setSubgoalMarkers();
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
		modal.find('.submit-delete-goal').data('parentId', data['parentId']);
	})

	$('.update-goal').live('click', function(e) {
		var modal = $($(this).attr('href'));
		var data = $(this).data();
		modal.find('input[name="goal-name"]').val(data['name']);
		modal.find('input[name="num-words"]').val(data['words']);
		modal.find('input[name="start-date"]').val(data['start']);
		modal.find('input[name="end-date"]').val(data['end']);
		if (data['end']) {
			modal.find('input[name="num-days"]').val(data['days']);
		} else {
			modal.find('input[name="num-days"]').val('');
		}
		if (data['time'] != '000000') {
			modal.find('input[name="start-now"]').prop('checked', true);
		} else {
			modal.find('input[name="start-now"]').prop('checked', false);
		}
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

	$('.subgoal-info-holder').live('mouseover', function() {
		$('.subgoal-marker-holder[data-id="' + $(this).data('id') + '"]').subgoalOverlayShow()
	});
	$('.subgoal-info-holder').live('mouseout', function() {
		$('.subgoal-marker-holder[data-id="' + $(this).data('id') + '"]').subgoalOverlayHide()
	});

	$.fn.extend({
		subgoalOverlayShow: function(e) {
			$(this).find('.subgoal-overlay').addClass('show').removeClass('hidden');
		},
		subgoalOverlayHide: function(e) {
			$(this).find('.subgoal-overlay').removeClass('show').addClass('hidden');
		}
	})
})

function errorCheckGoal(modal) {
	var error = 0;
	var name = modal.find('input[name="goal-name"]');
	error += errorCheck(name, name.val())
	var num = modal.find('input[name="num-words"]');
	error += errorCheck(num, !isNaN(num.val()) && num.val())
	var start = modal.find('input[name="start-date"]');
	error += errorCheck(start, !isNaN(new Date(start.val()).getTime()))
	return error;
}

function errorCheck(item, val) {
	if (val) {
		item.removeClass('error');
		return 0
	} else {
		item.addClass('error');
		return 1
	}
}



function setSubgoalMarkers(e) {
	$('.subgoal-marker').each(function() {
		var progress = $(this).parents('.progress')
		console.log($(this).data('perc'));
		var offset = progress.width() * ($(this).data('perc')/100);
		$(this).css({'left': progress.offset().left + offset + 'px'});
	});
	$('.subgoal-marker-holder').live('mouseover', function() {
		$(this).subgoalOverlayShow()
	});
	$('.subgoal-marker-holder').live('mouseout', function() {
		$(this).subgoalOverlayHide()
	});
	$('.subgoal-marker-holder').each(function() {
		var start = $(this).find('.subgoal-start');
		var end = $(this).find('.subgoal-end');
		var overlay = $(this).find('.subgoal-overlay');
		overlay.css({
			'left': start.offset().left,
			'width': end.offset().left - start.offset().left
		})
	})
}