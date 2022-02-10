const params = (new URL(location)).searchParams;
const id = params.get("id");

$.ajax(`/api/blog?id=${id}`).done(function (data){
    console.log("test");
    $("#title").text(data.title);
    $("#content").html(data["content"]);
});