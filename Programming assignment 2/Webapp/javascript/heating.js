const up_button = document.querySelector('.up');
const down_button = document.querySelector('.down');
const heating_txt = document.querySelector('.ht_temp');
const room_txt = document.querySelector('.rm_temp');

var config = {
    apiKey: "AIzaSyD7_7riZzk-shvS_HZ87zCkrutwRcXwjpI",
    authDomain: "home-41654.firebaseapp.com",
    // For databases not in the us-central1 location, databaseURL will be of the
    // form https://[databaseName].[region].firebasedatabase.app.
    // For example, https://your-database-123.europe-west1.firebasedatabase.app
    databaseURL: "https://home-41654-default-rtdb.europe-west1.firebasedatabase.app/",
    storageBucket: "bucket.appspot.com"
  };
firebase.initializeApp(config);

  // Get a reference to the database service
var database = firebase.database();
var ref = firebase.database().ref('/');

var heating_tmp = 0

ref.on('value', (snapshot) => {
    const data = snapshot.val()
    page_update(data['temperature']['heating temperature'], data['temperature']['room temperature'])
    heating_tmp = (data['temperature']['heating temperature'])
})






up_button.addEventListener('click', up_tmp);
down_button.addEventListener('click', down_tmp);

function data_update(temp) {
    firebase.database().ref('temperature/').update({
        'heating temperature' : temp
    })
}

function page_update(heating, room) {
    heating_txt.innerHTML = heating
    console.log(room)
    room_txt.innerHTML = room
}

function up_tmp() {
    heating_tmp = heating_tmp + 1
    heating_txt.innerHTML = heating_tmp
    data_update(heating_tmp)

}

function down_tmp() {
    heating_tmp = heating_tmp - 1
    heating_txt.innerHTML = heating_tmp
    data_update(heating_tmp)

}
