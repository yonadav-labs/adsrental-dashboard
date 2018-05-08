// http://localhost:9999/#host=ec2-34-216-109-97.us-west-2.compute.amazonaws.com&user=Administrator&password=AdsInc18rpid=RP999&connect=true

document.read
function clipboardPaste(str) {
    for (var i = 0; i < str.length; i++) {
        var char = str.charAt(i);
        vkbd.VKI_shift = true;
        vkbd.kpress(char.toUpperCase());
        vkbd.VKI_shift = false;
    }
}

function initializeClipboard() {
    $('clipboard_paste').addEvent('click', function(){
        var str = $('clipboard_content').get('value');
        console.log('clicked!' + str);
    });
}
