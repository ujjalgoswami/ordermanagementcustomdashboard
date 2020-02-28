(function () {
    const firebaseConfig = {
    apiKey: "AIzaSyBtoIEn1IWq2W7NmS0cG52QCrD_8IRSTmU",
    authDomain: "findsportsdashboard.firebaseapp.com",
    databaseURL: "https://findsportsdashboard.firebaseio.com",
    projectId: "findsportsdashboard",
    storageBucket: "findsportsdashboard.appspot.com",
    messagingSenderId: "857456854993",
    appId: "1:857456854993:web:f26cd6b187dbceefb342f0"
  };
    firebase.initializeApp(firebaseConfig);
    const announcement_div=document.getElementById('announcement');
     const ofBar=document.getElementById('ofBar');



    const preobject=document.getElementById('notificationsdiv');


    const dbrefobject=firebase.database().ref().child('notifications');


    const notificationCount=document.getElementById('notificationscount');


    const dbrefobject_announcement=firebase.database().ref().child('announcement');


    dbrefobject_announcement.on('value',snap=>{

   dict_status_announcement=snap.val()
        status=dict_status_announcement['active']
        announcement=dict_status_announcement['value']
        announcement_div.innerHTML=announcement
        if(status=='True'){
            $('#ofBar').attr('style','');
             $('#ofBar_temp').attr('style','');

        }
        else{
            $('#ofBar').attr('style','display: none;');
             $('#ofBar_temp').attr('style','display: none;');

        }

    });

    dbrefobject.on('value',snap=>{
            notification_string=""

            dict_of_notifications=snap.val()

            var keys = Object.keys(dict_of_notifications);

            for(var i = 0; i < keys.length;i++){

                notification_value=dict_of_notifications[keys[i]]['value']
                notification_link=dict_of_notifications[keys[i]]['link']
                notification_string+="<a  class='dropdown-item' href='"+notification_link+"'>"+notification_value+"</a>";
                }
            preobject.innerHTML=notification_string;
        notificationCount.innerHTML=keys.length;


    }







    );





}());