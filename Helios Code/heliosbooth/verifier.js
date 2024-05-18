// helper functions for verifying a ballot
// assumes all of Helios machinery is loaded

function verify_ballot(election_raw_json, encrypted_vote_json, status_cb) {
    var overall_result = true;
    try {
      console.log("verifying ballot");
      console.log(election_raw_json);
      console.log(encrypted_vote_json);
	election = HELIOS.Election.fromJSONString(election_raw_json);
	var election_hash = election.get_hash();
	// status_cb("election fingerprint is " + election_hash);
	
	// display ballot fingerprint
	encrypted_vote = HELIOS.EncryptedVote.fromJSONObject(encrypted_vote_json, election);
  if(status_cb != ""){
	status_cb("ballot tracker is " + encrypted_vote.get_hash());
  }
	
      // check the hash
    //   if (election_hash == encrypted_vote.election_hash) {
    //     //   status_cb("election fingerprint matches ballot");
    //   } else {
    //       overall_result = false;
    //     //   status_cb("PROBLEM = election fingerprint does not match");          
    //   }

          // check the hash
    if (!(election_hash == encrypted_vote.election_hash)) {
    overall_result = false;        
    }
      
      // display the ballot as it is claimed to be
      if(status_cb != ""){
        status_cb("Ballot Contents:");
      }
      _(election.questions).each(function(q, qnum) {
	      if (q.tally_type != "homomorphic") {
		//   status_cb("WARNING: the tally type for this question is not homomorphic. Verification may fail because this verifier is only set up to handle homomorphic ballots.");
	      }
        
	      var answer_pretty_list = _(encrypted_vote.encrypted_answers[qnum].answer).map(function(aindex, anum) {
		      return q.answers[aindex];
		  });
      if(status_cb != ""){
	      status_cb("Question #" + (qnum+1) + " - " + q.short_name + " : " + answer_pretty_list.join(", "));
      }
      });
      
    //   // verify the encryption
    //   if (encrypted_vote.verifyEncryption(election.questions, election.public_key)) {
    //     //   status_cb("Encryption Verified");
    //   } else {
    //       overall_result = false;
    //     //   status_cb("PROBLEM = Encryption doesn't match.");
    //   }

        // verify the encryption
        if (!(encrypted_vote.verifyEncryption(election.questions, election.public_key))) {
        overall_result = false;
      }
      
    //   if (encrypted_vote.verifyProofs(election.public_key, function(ea_num, choice_num, result) {
    //   })) {
    //     //   status_cb("Proofs ok."); 
    //   } else {
    //       overall_result = false;
    //     //   status_cb("PROBLEM = Proofs don't work.");
    //   }

    // verify the proofs
    if (!(encrypted_vote.verifyProofs(election.public_key, function(ea_num, choice_num, result) {
    }))) {
        overall_result = false;
    }

    } catch (e) {
      if(status_cb != ""){
        status_cb('problem parsing election or ballot data structures, malformed inputs: ' + e.toString());
      }
      overall_result=false;
    }

    return overall_result;
}
