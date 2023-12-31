function createStory() {
    var title = document.getElementById("title").value;
    var body = document.getElementById("body").value;

    axios({
        method: "POST",
        url: "/story/create",
        data: {
            title: title,
            body: body,
        },
        headers: {
            "Content-Type": "application/json",
        }
    }).then(
        (response) => {
            var data = response.data;
            if (data.redirect) {
                // redirect exists, then set the URL to the redirect
                window.location.href = data.redirect;
            }

            if (data.status == 500) {
                alert(data.error);
                window.location.href = "/";  // redirect to home page
            }
        },
    )
}

function deleteStory(id, title) {
    var message = "Are you sure to delete story with title " + title + " ?";
    var confirm_delete = confirm(message);

    // value of confirm() function is True if user clicks on OK
    if (confirm_delete == true) {
        // use axios to call delete, with the story id to delete
        var url = "/story/delete/" + id;
        axios({
            method: "POST",
            url: url,
        }).then(
            (response) => {
                var data = response.data;
                if (data.redirect) {
                    window.location.href = data.redirect;
                }
            }
        );
    }
}

function register(){
    ;
}