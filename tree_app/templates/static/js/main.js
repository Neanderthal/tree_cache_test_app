/* eslint-disable no-console */
/* eslint-disable camelcase */

// Init left tree
$(() => {
    $('#left_tree').jstree({
    core: {
      data: {
        url: api_cache_tree_url,
        data(node) {
          return { id: node.id };
        },
      },
    },
  });
});
// Init right tree
$(() => {
  $('#right_tree').jstree({
    core: {
      data: {
        url: api_main_tree_url,
        data(node) {
          return { id: node.id };
        },
      },
    },
  });
});
// MOVE NODE
$(() => {
  $('#move_button').on('click', () => {
    const right_tree = $('#right_tree').jstree(true);
    const node = right_tree.get_selected()[0];
    $.ajax({
      url: api_move_node_url,
      data: {
        id: node,
      },
      type: 'PUT',
      success(result) {
        console.log(result);
        const left_tree = $('#left_tree').jstree(true);
        left_tree.load_node('#', () => {
          left_tree.open_all();
        });
      },
    });
  });
});
// DELETE NODE
$(() => {
  $('#delete_button').on('click', () => {
    const left_tree = $('#left_tree').jstree(true);
    const node = left_tree.get_selected()[0];
    if (node !== undefined) {
      $.ajax({
        url: api_delete_node_url,
        data: {
          id: node,
        },
        type: 'DELETE',
        success(result) {
          console.log(result);
          left_tree.load_node('#', () => {
            left_tree.open_all();
          });
        },
      });
    } else {
      $("#alert").text("You have to select node to delete!");
      $('#alert_box').addClass("show")
      console.log('Select parent node!');
      let myGreeting = setTimeout(() => {
        $('#alert_box').removeClass("show")
      }, 4000);
    }
  });
});
// ADD NODE
$(() => {
  $('#add_button').on('click', () => {
    const input_data = $('#input_data').val();
    const left_tree = $('#left_tree').jstree(true);
    const parent_node = left_tree.get_selected()[0];
    if (parent_node !== undefined) {
      $.ajax({
        url: api_add_node_url,
        data: {
          parent_node_id: parent_node,
          input_data,
        },
        type: 'PUT',
        success(result) {
          console.log(result);
          left_tree.load_node('#', () => {
            left_tree.open_all();
          });
        },
      });
    } else {
      $("#alert").text("You have to select parent node!");
      $('#alert_box').addClass("show")
      console.log('Select parent node!');
      let myGreeting = setTimeout(() => {
        $('#alert_box').removeClass("show")
      }, 4000);
    }
  });
});
// FLUSH TREE
$(() => {
  $('#flush_button').on('click', () => {
    $.ajax({
      url: api_flush_url,
      data: {},
      type: 'POST',
      success(result) {
        const right_tree = $('#right_tree').jstree(true);
        right_tree.load_node('#');
        const left_tree = $('#left_tree').jstree(true);
        left_tree.load_node('#', () => {
          left_tree.open_all();
        });
        console.log(result);
      },
    });
  });
});
// RESET CACHE TREE
$(() => {
  $('#reset_button').on('click', () => {
    $.ajax({
      url: api_reset_url,
      data: {},
      type: 'POST',
      success(result) {
        const right_tree = $('#right_tree').jstree(true);
        right_tree.load_node('#');
        const left_tree = $('#left_tree').jstree(true);
        left_tree.load_node('#', () => {
          left_tree.open_all();
        });

        console.log(result);
      },
    });
  });
});

// EDIT TREE NODE
$(() => {
  $('#edit_button').on('click', () => {
    const left_tree = $('#left_tree').jstree(true);
    const selected_node = left_tree.get_selected(true)[0];
    $('#edit_data').val(selected_node.text)
    $('#edit_data').attr("data", selected_node.id);

    $('#edit_data').addClass("show")
  });
});

$(()=>{
  $('#edit_data').on("keypress", (e) => {
    if(e.which == 13) {
      $.ajax({
        url: api_update_node_url,
        data: {
          id: $('#edit_data').attr("data"),
          input_data: $('#edit_data').val(),
        },
        type: 'POST',
        success(result) {
          const left_tree = $('#left_tree').jstree(true);
          console.log(result);

          left_tree.load_node('#', () => {
            left_tree.open_all();
          });

          $('#edit_data').val("")
          $('#edit_data').removeClass("show")
        },
      });
    }
   
  })
})
