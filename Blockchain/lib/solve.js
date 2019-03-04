'use strict';
var NS = 'org.acme.mynetwork';

/**
 * Track the solving of puzzle by some user
 * @param {org.acme.mynetwork.SolvePuzzle} solve puzzle - the solving to be processed
 * @transaction
 */
function solvePuzzle(solve) {
    solve.puzzle.prize.owner = solve.solver;
    solve.puzzle.status = "closed";
  
    getAssetRegistry('org.acme.mynetwork.Artifact').then(function(assetRegistry) {
        getAssetRegistry('org.acme.mynetwork.Puzzle').then(function(assetRegistry) {
    	  return assetRegistry.update(solve.puzzle);
        });
    	return assetRegistry.update(solve.puzzle.prize);
    });
}

/**
 * Track the trade of a commodity from one trader to another
 * @param {org.acme.mynetwork.Trade} trade - the trade to be processed
 * @transaction
 */
function tradeArtifact(trade) {
    trade.offer.autor.balance += trade.offer.artifact.cost;
    trade.offer.recipient.balance -= trade.offer.artifact.cost;
    trade.offer.artifact.owner = trade.offer.recipient;
    trade.offer.status = "closed";

    getAssetRegistry('org.acme.mynetwork.Artifact').then(function(assetRegistry) {
      	getParticipantRegistry('org.acme.mynetwork.Character').then(function(participantRegistry) {
          	getParticipantRegistry('org.acme.mynetwork.Character').then(function(participantRegistry) {
              	getAssetRegistry('org.acme.mynetwork.Offer').then(function(assetRegistry) {
    				return assetRegistry.update(trade.offer);
    			});
    			return participantRegistry.update(trade.offer.recipient);
    		});
    		return participantRegistry.update(trade.offer.autor);
    	});
    	return assetRegistry.update(trade.offer.artifact);
    });
}
