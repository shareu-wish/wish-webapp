

$('#firstSection').mousemove(function(e) {
    const x = e.pageX - this.offsetLeft;
    const y = e.pageY - this.offsetTop;

    $(this).css({ '--mouse-x': `${x}px`, '--mouse-y': `${y}px` });
})
