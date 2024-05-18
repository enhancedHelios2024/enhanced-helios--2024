
const getCookie = (name) => {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
};

const component = document.getElementsByTagName("face-liveness")[0];



function listener(event) {
  if (
    event.detail.action === "PROCESS_FINISHED" &&
    event.detail.data.status === 1 && event.detail.data.response.code == 0
  ) {
    // hoow to get the user in the session
    $('#loading').show();
    const response = event.detail.data.response;
    console.log("response : ", response.images[0]);

    if (userData.server_user_face_share) {
      console.log("USER HAS SHARES");
      console.log(userData);
      $.ajax({
        type: 'GET',
        url: '../get_other_shares/',
        data: userData.profile,
        success: function(data) {
          var c1 = data.c1;
          var c2 = data.c2;
          var r1 = data.r1;
          console.log("c1:", c1);
          console.log("c2:", c2);
          console.log("r1:", r1);

          var c1_list_initial = c1.split(" "); // Assuming each line contains a number
          var c1_list_last_element = c1_list_initial[c1_list_initial.length - 1];
          var c1_list_array = c1_list_initial.slice(0, -1).map(Number);
          c1_list_array.push(c1_list_last_element);

          var c2_list_initial = c2.split(" "); // Assuming each line contains a number
          var c2_list_last_element = c2_list_initial[c2_list_initial.length - 1];
          var c2_list_array = c2_list_initial.slice(0, -1).map(Number);
          c2_list_array.push(c2_list_last_element);

          var r1_list_array = r1.split(" ").map(Number);

          $.ajax({
            type: "POST",
            url: "../recombine_shares/",
            data: JSON.stringify({
              file1Array: c1_list_array,
              file2Array: c2_list_array,
              file3Array: r1_list_array,
              mainResponse: response.images[0],
            }),
            success: function (data) {
              $('#loading').hide();
              if (data.redirect_url) {
                  if (data.message) {
                      alert(data.message); 
                  }
                  window.location.href = data.redirect_url;  // Redirect to the specified URL
              } else {
                  if (data.message) {
                      alert(data.message); 
                      window.location.href = '/auth/facial_recognition/';
                  }
                  console.log(data); 
              }
            },
            error: function (xhr, status, error) {
              // Handle errors
              console.error(xhr.responseText);
              $('#loading').hide();
            },
          });
        },
        error: function(xhr, status, error) {
            console.error('Error fetching data:', error);
        }
      });
    }
    else {
      $('#loading').show();
      $.ajax({
        type: "POST",
        url: "../classify_face/",  // Replace with the correct URL mapping for your view
        data: {
          response: response.images[0],
        },  // You can pass any necessary data to the view
        success: function (data) {
          console.log("REDIRECTING TO " + data.redirect_url);
          window.location.href = data.redirect_url;  // Redirect to the specified URL
          console.log("REDIRECTING TO " + data.redirect_url);
          if (data.message1) {
            $('#loading').hide();
            // alert(data.message2);
            // if(data.redirect_url === '/'){
            alert(data.message1);
            // }
          }
      },
      error: function (xhr, status, error) {
          // Handle errors
          console.error(xhr.responseText);
      },
    });
    }


  } else if (event.detail.data.response.code != 0){
    console.log("FAILED");
    // alert("Error occured. Please try again.")
    // window.location.href = '/auth/facial_recognition/';
  }
}

component.addEventListener("face-liveness", listener);

