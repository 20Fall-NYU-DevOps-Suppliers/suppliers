$(function() {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#supplier_id").val(res._id);
        $("#supplier_name").val(res.name);
        $("#supplier_like_count").val(res.like_count);
        $("#supplier_products").val(res.products);
        $("#supplier_rating").val(res.rating);
        if (res.is_active == true) {
            $("#supplier_is_active").val("true");
        } else if (res.is_active == false) {
            $("#supplier_is_active").val("false");
        } else {
            $("#supplier_is_active").val("None");
        }
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#supplier_name").val("");
        $("#supplier_like_count").val("");
        $("#supplier_products").val("");
        $("#supplier_rating").val("");
        $("#supplier_is_active").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Supplier
    // ****************************************

    $("#create-btn").click(function() {

        var name = $("#supplier_name").val();
        var like_count = $("#supplier_like_count").val();
        var is_active_str = $("#supplier_is_active").val();
        var products = $("#supplier_products").val();
        var rating = $("#supplier_rating").val();

        var is_active;
        if (is_active_str == "true") {
            is_active = true;
        } else if (is_active_str == "false") {
            is_active = false;
        } else {
            is_active = null;
        }

        var data = {
            "name": name,
            "like_count": like_count,
            "is_active": is_active,
            "products": products,
            "rating": rating
        };

        var ajax = $.ajax({
            type: "POST",
            url: "/suppliers",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res) {
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res) {
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Supplier
    // ****************************************

    $("#update-btn").click(function() {

        var name = $("#supplier_name").val();
        var like_count = $("#supplier_like_count").val();
        var is_active_str = $("#supplier_is_active").val();
        var products = $("#supplier_products").val();
        var rating = $("#supplier_rating").val();
        var supplier_id = $("#supplier_id").val();

        var is_active;
        if (is_active_str == "true") {
            is_active = true;
        } else if (is_active_str == "false") {
            is_active = false;
        } else {
            is_active = null;
        }

        var data = {
            "name": name,
            "like_count": like_count,
            "is_active": is_active,
            "products": products,
            "rating": rating
        };

        var ajax = $.ajax({
            type: "PUT",
            url: "/suppliers/" + supplier_id,
            contentType: "application/json",
            data: JSON.stringify(data)
        })

        ajax.done(function(res) {
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res) {
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Like a Supplier
    // ****************************************

    $("#like-btn").click(function() {

        var supplier_id = $("#supplier_id").val();
        var ajax = $.ajax({
            type: "PUT",
            url: "/suppliers/" + supplier_id + "/like",
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res) {
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res) {
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Supplier
    // ****************************************

    $("#retrieve-btn").click(function() {

        var supplier_id = $("#supplier_id").val();

        var ajax = $.ajax({
            type: "GET",
            url: "/suppliers/" + supplier_id,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res) {
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res) {
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Supplier
    // ****************************************

    $("#delete-btn").click(function() {

        var supplier_id = $("#supplier_id").val();

        var ajax = $.ajax({
            type: "DELETE",
            url: "/suppliers/" + supplier_id,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res) {
            clear_form_data()
            flash_message("Supplier has been Deleted!")
        });

        ajax.fail(function(res) {
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function() {
        $("#supplier_id").val("");
        clear_form_data()
    });

    // ****************************************
    // Search for a Supplier
    // ****************************************

    $("#search-btn").click(function() {

        var name = $("#supplier_name").val();
        var like_count = $("#supplier_like_count").val();
        var is_active_str = $("#supplier_is_active").val();
        var products = $("#supplier_products").val();
        var rating = $("#supplier_rating").val();
        var queryString = ""

        var is_active;
        if (is_active_str == "true") {
            is_active = true;
        } else if (is_active_str == "false") {
            is_active = false;
        } else {
            is_active = null;
        }


        if (name) {
            queryString += 'name=' + name
        }
        if (like_count) {
            if (queryString.length > 0) {
                queryString += '&like_count=' + like_count
            } else {
                queryString += 'like_count=' + like_count
            }
        }
        if (is_active != null) {
            if (queryString.length > 0) {
                queryString += '&is_active=' + is_active
            } else {
                queryString += 'is_active=' + is_active
            }
        }
        if (products) {
            if (queryString.length > 0) {
                queryString += '&product_id=' + products
            } else {
                queryString += 'product_id=' + products
            }
        }
        if (rating) {
            if (queryString.length > 0) {
                queryString += '&rating=' + rating
            } else {
                queryString += 'rating=' + rating
            }
        }

        var ajax = $.ajax({
            type: "GET",
            url: "/suppliers?" + queryString,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res) {
            //alert(res.toSource())
            $("#search_results").empty();
            $("#search_results").append('<table class="table-striped" cellpadding="10">');
            var header = '<tr>'
            header += '<th style="width:10%">ID</th>'
            header += '<th style="width:10%">Name</th>'
            header += '<th style="width:10%">Like_count</th>'
            header += '<th style="width:10%">Is_active</th>'
            header += '<th style="width:10%">Products</th>'
            header += '<th style="width:10%">Rating</th></tr>'
            $("#search_results").append(header);
            var firstSupplier = "";
            for (var i = 0; i < res.length; i++) {
                var supplier = res[i];
                var row = "<tr><td>" + supplier._id + "</td><td>" + supplier.name + "</td><td>" + supplier.like_count + "</td><td>" + supplier.is_active + "</td><td>" +
                    supplier.products + "</td><td>" + supplier.rating + "</td></tr>";
                $("#search_results").append(row);
                if (i == 0) {
                    firstSupplier = supplier;
                }
            }

            $("#search_results").append('</table>');

            // copy the first result to the form
            if (firstSupplier != "") {
                update_form_data(firstSupplier)
            }

            flash_message("Success")
        });

        ajax.fail(function(res) {
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Recommend a Supplier
    // ****************************************

    $("#recommend-btn").click(function() {

        var product_id = $("#supplier_products").val();

        var ajax = $.ajax({
            type: "GET",
            url: "/suppliers/" + product_id + "/recommend",
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res) {
            $("#search_results").empty();
            $("#search_results").append('<table class="table-striped" cellpadding="10">');
            var header = '<tr>'
            header += '<th style="width:10%">ID</th>'
            header += '<th style="width:10%">Name</th>'
            header += '<th style="width:10%">Like_count</th>'
            header += '<th style="width:10%">Is_active</th>'
            header += '<th style="width:10%">Products</th>'
            header += '<th style="width:10%">Rating</th></tr>'
            $("#search_results").append(header);

            var supplier = res;
            if (supplier != "") {
                console.log("supplier is: " + supplier._id + "," + supplier.name + "," + supplier.products)
                var row = "<tr><td>" + supplier._id + "</td><td>" + supplier.name + "</td><td>" + supplier.like_count + "</td><td>" + supplier.is_active + "</td><td>" +
                    supplier.products + "</td><td>" + supplier.rating + "</td></tr>";
                $("#search_results").append(row);
                $("#search_results").append('</table>');
                update_form_data(supplier)
            }

            flash_message("Success")
        });


        ajax.fail(function(res) {
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

})