function mobile_search(query_element, get_base_url_callback, hide_type)
{
	hide_type = hide_type || false;
	query_element = $(query_element);
	let results_target = $(query_element.data('search-results-target')).html('');
	let query = query_element.val();
	if(query.length < 2)
		return;
	let search_base = query_element.data('search-base');
	let result_count = 0;
	let matching_regular_expression = new RegExp(query, 'i');
	let results = '<div class="list-group">';
	$.each(search_base, function(item_index, item)
	{
		if(matching_regular_expression.test(item.name))
		{
			let item_display = item.name;
			if(!hide_type && item.type)
			{
				item_display += '<br><span style="font-size:small; font-weight:bold;">' + item.type.capitalize() + '</span>';
			}
			results += '<a href="' + get_base_url_callback(item.type, item.id) + '" class="list-group-item list-group-item-info">' + item_display + '</a>';
			result_count++;
		}
	});
	results += '</div>';
	if(result_count > 0)
	{
		results_target.html(results);
	}
}