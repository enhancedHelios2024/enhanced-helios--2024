// import { initializeApp } from "firebase/app";
// import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyBq8gua8yF8GRAl2SB9jBXHDaynsZICTc0",
  authDomain: "helioscan-helios.firebaseapp.com",
  databaseURL: "https://helioscan-helios-default-rtdb.firebaseio.com",
  projectId: "helioscan-helios",
  storageBucket: "helioscan-helios.appspot.com",
  messagingSenderId: "137838190489",
  appId: "1:137838190489:web:2c9e600bb2fecbc07cbd08",
  measurementId: "G-ZLP0DTQ9N8",
};
firebase.initializeApp(firebaseConfig);

var db = firebase.database();

function saveVerificationResult(
  verificationResult,
  ballot_tracker,
  election_uuid
) {
  console.log(
    "received verification result: " +
      verificationResult +
      " for ballot: " +
      ballot_tracker
  );
  // Get a reference to the database service
  var database = firebase.database();

  // Reference to the audit_trial collection
  var sanitizedBallotTracker = ballot_tracker.replace(/\//g, "_");
  var verificationResultRef = database
    .ref("ballot_trackers")
    .child(election_uuid)
    .child(sanitizedBallotTracker);

  // Set data
  // verificationResultRef.set({
  //     verificationResult: verificationResult
  // }, function(error) {
  //     if (error) {
  //         console.error("Data could not be saved: " + error);
  //     } else {
  //         console.log("Data saved successfully.");
  //     }
  // });
  verificationResultRef.once("value", function (snapshot) {
    if (snapshot.exists()) {
      // Set data
      verificationResultRef.set(
        {
          verificationResult: verificationResult,
        },
        function (error) {
          if (error) {
            console.error("Data could not be saved: " + error);
          } else {
            console.log("Data saved successfully.");
          }
        }
      );
    } else {
      console.log("Branch of ballot_tracker does not exist.");
    }
  });
}
// Initialize Firebase
// const app = initializeApp(firebaseConfig);
// const analytics = getAnalytics(app);
//   window.onload = function() {
//       save();
//   };

$(document).ready(function () {
  BigInt.setup(
    function () {
      //    $('#verifier_loading').hide();

      if (BigInt.is_dummy) {
        //   $('#dummy_bigint').show();
        return;
      }

      //    $('#verifier').show();
      //    var election_url = $.query.get('election_url');
      //    $('#election_url').val(election_url);
      // var election_url = BOOTH.election_url;
    },
    function () {
      //    $('#dummy_bigint').show();
    }
  );
});

// function result_append(str) {
// $('#results').append(str).append("<br />");
// }

// function result_empty() {
//     $('#results').empty();
//   }

// function verify_single_ballot(election_url, audit_trail) {
//   var encrypted_vote_json = jQuery.secureEvalJSON(audit_trail);

// //   result_empty()

// //   result_append("loading election...");

//   // quick and dirty detection of cast ballot
//   if (encrypted_vote_json['cast_at']) {
//     // result_append("\n\nIt looks like you are trying to verify a cast ballot. That can't be done, only audited ballots can be verified.");
//     return;
//   }

// //   $('#loading').show();

//   var after_computation = function(overall_result) {
//     // result_append("<br />");

//     // $('#loading').hide();

//     if (overall_result) {
//       //  result_append('SUCCESSFUL VERIFICATION, DONE!');
//        alert('SUCCESSFUL VERIFICATION, DONE!')

//     } else {
//       //  result_append('PROBLEM - THIS BALLOT DOES NOT VERIFY.');
//        alert('VERIFICATION FAILED')

//     }

//   };

//   // the hash will be computed within the setup function call now
//   $.ajax({url: election_url, success: function(raw_json) {
//     if (window.Worker) {
//       var verifier_worker = new window.Worker("verifierworker.js");
//       verifier_worker.onmessage = function(event) {
//         if (event.data.type == 'log')
//           return console.log(event.data.msg);

//         if (event.data.type == 'status')
//         //   return result_append(event.data.msg);

//         if (event.data.type == 'result')
//           return after_computation(event.data.result);
//       };

//       verifier_worker.postMessage({'type':'verify', 'election':raw_json, 'vote':encrypted_vote_json});
//     } else {
//       var overall_result = verify_ballot(raw_json, encrypted_vote_json, result_append);
//       return overall_result;
//     //   after_computation(overall_result);
//     }
//   }, error: function() {
//     // result_empty()
//     // $('#loading').hide();
//     alert('PROBLEM LOADING election. Are you sure you have the right election URL?' + '\n' + '\n' +'THIS BALLOT DOES NOT VERIFY.');

//       // result_append('PROBLEM LOADING election. Are you sure you have the right election URL?<br />');
//       // result_append('PROBLEM - THIS BALLOT DOES NOT VERIFY.');
//   }
//   });
// }
function verify_single_ballot(election_url, audit_trail) {
  return new Promise((resolve, reject) => {
    var encrypted_vote_json = jQuery.secureEvalJSON(audit_trail);

    if (encrypted_vote_json["cast_at"]) {
      reject(
        new Error(
          "It looks like you are trying to verify a cast ballot. That can't be done, only audited ballots can be verified."
        )
      );
      return;
    }

    $.ajax({
      url: election_url,
      success: function (raw_json) {
        if (window.Worker) {
          var verifier_worker = new window.Worker("verifierworker.js");
          verifier_worker.onmessage = function (event) {
            if (event.data.type == "log") return console.log(event.data.msg);
            if (event.data.type == "status") return console.log(event.data.msg); // Modify as needed
            if (event.data.type == "result") resolve(event.data.result);
          };

          verifier_worker.postMessage({
            type: "verify",
            election: raw_json,
            vote: encrypted_vote_json,
          });
        } else {
          var overall_result = verify_ballot(
            raw_json,
            encrypted_vote_json,
            result_append
          );
          resolve(overall_result);
        }
      },
      error: function () {
        reject(
          new Error(
            "PROBLEM LOADING election. Are you sure you have the right election URL?\n\nTHIS BALLOT DOES NOT VERIFY."
          )
        );
      },
    });
  });
}

// SECOND CHANGE MADE BY KHALID - SAVE RANDOMNESS HASH
function saveRandomnessHash(randomness_hash, ballot_tracker) {
  console.log("randomness_hash: " + randomness_hash);
  console.log("==============================");
  // Get a reference to the database service
  var database = firebase.database();

  var randomnessHashRef = database.ref("randomness_hash");

  // Set data
  randomnessHashRef.child(randomness_hash).set(
    {
      randomness_hash: randomness_hash,
      ballot_tracker: ballot_tracker,
    },
    function (error) {
      if (error) {
        console.error("Data could not be saved: " + error);
      } else {
        console.log("Data saved successfully.");
      }
    }
  );
}
