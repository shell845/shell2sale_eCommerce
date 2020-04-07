$(document).ready(function(){
      // Contact Form
      var contactForm = $(".contact-form")
      var contactFormMethod = contactForm.attr("method")
      var contactFormEndpoint = contactForm.attr("action")
      contactForm.submit(function(event){
        event.preventDefault()
        var contactFormData = contactForm.serialize();
        var thisForm = $(this);
        $.ajax({
          url: contactFormEndpoint,
          method: contactFormMethod,
          data: contactFormData,
          success: function(data){
            thisForm[0].reset()
            $.alert({
              title: "Thanks ^_^",
              content: "Thank you for your message, we will back to you soon",
              theme: "modern",
            })
          },
          error: function(errorData){
            var jsonData = errorData.responseJSON
            var msg = ""

            $.each(jsonData, function(key, value){ // jsonData is dict so use (key, value) array here
              msg += key + ": " + value[0].message
            })

            $.alert({
              title: "SORRY *_* sth wrong",
              content: msg,
              theme: "modern",
            })
            console.log("Submit contact error")
            console.log(errorData)
          }
        })
      })

      // Auto Search
      var searchForm = $(".search-form");
      var searchInput = searchForm.find("[name='q']");
      var typingTimer;
      var typingInterval = 500; // ms
      var searchBtn = searchForm.find("[type='submit']");

      // release key
      searchInput.keyup(function(event){
        clearTimeout(typingTimer)
        typingTimer = setTimeout(perfomSearch, typingInterval)
      })

      // press down key
      searchInput.keydown(function(event){
        clearTimeout(typingTimer)
      })

      function displaySearching(){
        searchBtn.addClass("disabled")
        searchBtn.html("<i class='fa fa-spin fa-spinner'></i> Searching...")
      }

      function perfomSearch(){
        displaySearching()
        var query = searchInput.val()
        setTimeout(function(){
          window.location.href='/search/?q=' + query
        }, 500)
        
      }

      // Update Cart
      var productForm = $(".form-product-ajax")

      productForm.submit(function(event){
        event.preventDefault();
        var thisForm = $(this); //grab data from the form
        //var actionEndpoint = thisForm.attr("action");
        var actionEndpoint = thisForm.attr("data-endpoint"); //ensure the webpage works even user disable javascript
        var httpMethod = thisForm.attr("method");
        var formData = thisForm.serialize();

        $.ajax({
          url: actionEndpoint,
          method: httpMethod,
          data: formData,
          success: function(data){
            var submitSpan = thisForm.find(".submit-span")
            if (data.added){
              submitSpan.html("<button type='submit' class='btn btn-warning'>Remove from cart</button>")
            } else {
              submitSpan.html("<button type='submit' class='btn btn-success'>Add to cart</button>")
            }
            var navbarCount = $(".navbar-cart-count")
            navbarCount.text(data.cartItemCount)
            var currentPath = window.location.href
            if (currentPath.indexOf("cart") != -1) {
              refreshCart()
            }
          },
          error: function(errorData){
            $.alert({
              title: "SORRY *_*",
              content: "An error occurred, please try later",
              theme: "modern",
            })
            console.log("Submit cart error")
            console.log(errorData)
          }
        })
      })

      function refreshCart(){
        console.log("*** in cart")
        var cartTable = $(".cart-table")
        var cartBody = cartTable.find(".cart-body")
        var productRows = cartBody.find(".cart-product")
        var currentUrl = window.location.href

        var refreshCartUrl = "/api/cart/";
        var refreshCartMethod = "GET";
        var data = {};

        $.ajax({
          url: refreshCartUrl,
          method: refreshCartMethod,
          data: data,
          success: function(data){
            // console.log("refresh cart success")
            // console.log(data)
            var hiddenCartItemRemoveForm = $(".cart-item-remove-form")
            itemNum = data.products.length 
            if (itemNum > 0){
              productRows.html(" ")          
              $.each(data.products.reverse(), function(index, value){
                // console.log(value)
                var newCartItemRemove = hiddenCartItemRemoveForm.clone()
                newCartItemRemove.css("display", "block")
                // newCartItemRemove.removeClass("hidden-class")
                newCartItemRemove.find(".cart-item-product-id").val(value.id)
                cartBody.prepend("<tr><th scope=\"row\">" + itemNum + "</th><td><a href='" + value.url + "'>" + value.title + "</a></td><td>" + newCartItemRemove.html() + "</td><td>" + value.price + "</td></tr>")
                itemNum --
              })

              cartBody.find(".cart-subtotal").text(data.subtotal)
              cartBody.find(".cart-total").text(data.total)
            } else {
              window.location.href = currentUrl
            }
          },
          error: function(errorData){
            $.alert({
              title: "SORRY *_*",
              content: "An error occurred, please try later",
              theme: "modern",
            })
            console.log("refresh cart error")
            console.log(errorData)
          }
        })
      }

    })