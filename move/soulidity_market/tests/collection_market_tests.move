#[test_only]
module soulidity_market::collection_market_tests_owned_transport_v1;
use std::string;
use sui::test_scenario::{Self,Scenario};
use sui::kiosk::{Self,Kiosk};
use sui::transfer_policy::{Self,TransferPolicy};
use sui::coin::{Self,Coin};
use sui::clock::{Self,Clock};
use soulidity_v1::fixtures::{Self,USD};
use soulidity_foundation::economics::{Self,Config,Admin};
use soulidity_v1::custody;
use soulidity_custody::account::Account;
use soulidity_v1::collection;
use soulidity_collection::collection::{Collection,Factory,Right,Listing};
use soulidity_application::character::{Self as soul};
use soulidity_standard::soul::Soul;
use soulidity_market::market;
public struct F {sc:Scenario,c:Collection,k:Kiosk,a:Account,cfg:Config<USD>,factory:Factory,policy:TransferPolicy<Right>,clock:Clock,s:Soul,spare:Soul}

fun setup(extra:u16,tradeable:bool,max:Option<u64>,floor:Option<u128>,other_creator:bool):F {
    let mut sc=soulidity_v1::market::setup_for_testing(0,0,0,0,0,0);collection::init_for_testing(sc.ctx());let kid=custody::create(sc.ctx());let sid=fixtures::mint(&mut sc,71,0);sc.next_tx(if(other_creator)@0xc else @0xb);let spare_id=fixtures::mint(&mut sc,72,0);sc.next_tx(if(other_creator)@0xc else @0xb);let spare:Soul=sc.take_from_sender_by_id(spare_id);transfer::public_transfer(spare,@0xb);sc.next_tx(@0xb);
    let cfg:Config<USD> = sc.take_shared();let factory:Factory=sc.take_shared();let policy:TransferPolicy<Right> = sc.take_shared();let mut k:Kiosk=sc.take_shared_by_id(kid);let mut a:Account=sc.take_from_sender();let clock=clock::create_for_testing(sc.ctx());
    let cid=collection::create(&factory,&policy,&cfg,&mut k,&mut a,string::utf8(b"Collection"),string::utf8(b"Original members"),string::utf8(b"https://example.invalid/cover"),extra,tradeable,max,floor,0,1000,&clock,sc.ctx());sc.next_tx(@0xb);let c:Collection=sc.take_shared_by_id(cid);let s:Soul=sc.take_from_sender_by_id(sid);let spare:Soul=sc.take_from_sender_by_id(spare_id);F{sc,c,k,a,cfg,factory,policy,clock,s,spare}
}

fun normal():F{setup(2000,true,option::some(2),option::some(1000),false)}

fun add(f:&mut F,cr:u64,sr:u64){collection::add_soul(&mut f.c,&mut f.s,cr,sr,f.sc.ctx())}

public struct T {sc:Scenario,c:Collection,k:Kiosk,a:Account,cfg:Config<USD>,factory:Factory,policy:TransferPolicy<Right>,clock:Clock,spare:Soul}

fun list_member(f:F):(T,ID,ID) {
    let F{mut sc,mut c,k,a,cfg,factory,policy,clock,mut s,spare}=f;let id=object::id(&s);soul::grant(&mut s,@0xe,1,option::none(),0,option::none(),&clock,sc.ctx());collection::add_soul(&mut c,&mut s,0,1,sc.ctx());soul::unmount_bound(&mut s,b"bound",2);let h=soul::manifest_hash(&s);let lid=market::list_soul_with_collection(s,&c,&cfg,101,1000,3,h,0,&clock,sc.ctx());(T{sc,c,k,a,cfg,factory,policy,clock,spare},lid,id)
}

fun end_t(t:T){let T{sc,c,k,a,cfg,factory,policy,clock,spare}=t;test_scenario::return_shared(c);test_scenario::return_shared(k);test_scenario::return_shared(cfg);test_scenario::return_shared(factory);test_scenario::return_shared(policy);sc.return_to_sender(a);sc.return_to_sender(spare);clock::destroy_for_testing(clock);sc.end();}

fun transfer_right(t:&mut T) {
    let id=collection::list(&t.c,&mut t.k,&mut t.a,&t.cfg,100,1000,0,0,&t.clock,t.sc.ctx());t.sc.next_tx(@0xc);let buyer=custody::create(t.sc.ctx());t.sc.next_tx(@0xc);let mut k:Kiosk=t.sc.take_shared_by_id(buyer);let mut a:Account=t.sc.take_from_sender();let mut l:Listing<USD> = t.sc.take_shared_by_id(id);let q=collection::quote(&l,&t.cfg,@0xc);let payment=coin::mint_for_testing<USD>(105,t.sc.ctx());collection::buy(&mut l,&mut t.c,&t.factory,&t.policy,&mut t.k,&mut k,&mut a,&mut t.cfg,0,0,0,q,fixtures::h(80),payment,&t.clock,t.sc.ctx());test_scenario::return_shared(k);test_scenario::return_shared(l);t.sc.return_to_sender(a);t.sc.next_tx(@0xb);
}

fun buy_member(t:&mut T,l:&mut market::Listing<Soul,USD>,snapshot:vector<u8>) {
    let h=market::manifest_hash(l);let total=market::collection_total(l,&t.c,&t.cfg);assert!(total==140,0);let payment=coin::mint_for_testing<USD>(total,t.sc.ctx());let q=market::collection_quote_hash(l,&t.c,&t.cfg,t.sc.sender());market::buy_soul_with_collection(l,&t.c,&mut t.cfg,0,h,snapshot,q,0,fixtures::h(81),payment,&t.clock,t.sc.ctx())
}

fun wrong_buyer_member_quote(t:&mut T,l:&mut market::Listing<Soul,USD>){let h=market::manifest_hash(l);let snapshot=collection::snapshot_hash(&t.c);let q=market::collection_quote_hash(l,&t.c,&t.cfg,@0x9);let payment=coin::mint_for_testing<USD>(140,t.sc.ctx());market::buy_soul_with_collection(l,&t.c,&mut t.cfg,0,h,snapshot,q,0,fixtures::h(81),payment,&t.clock,t.sc.ctx())}

fun plain_buy(t:&mut T,l:&mut market::Listing<Soul,USD>){let h=market::manifest_hash(l);let payment=coin::mint_for_testing<USD>(101,t.sc.ctx());market::buy_soul(l,&mut t.cfg,0,h,fixtures::h(99),0,fixtures::h(81),payment,&t.clock,t.sc.ctx())}

fun sum_coins(sc:&Scenario):u64{let ids=sc.ids_for_sender<Coin<USD>>();let mut total=0;ids.do_ref!(|id|{let c:Coin<USD> = sc.take_from_sender_by_id(*id);total=total+coin::value(&c);sc.return_to_sender(c)});total}

#[test]
#[expected_failure(abort_code=4,location=soulidity_market::market)]
fun collection_member_cannot_use_unbundled_soul_listing(){let mut f=normal();add(&mut f,0,0);let F{mut sc,c,k,a,cfg,factory,policy,clock,s,spare}=f;let h=soul::manifest_hash(&s);market::list_soul(s,&cfg,101,1000,1,h,0,&clock,sc.ctx());test_scenario::return_shared(c);test_scenario::return_shared(k);test_scenario::return_shared(cfg);test_scenario::return_shared(factory);test_scenario::return_shared(policy);sc.return_to_sender(a);sc.return_to_sender(spare);clock::destroy_for_testing(clock);sc.end();}

#[test]
#[expected_failure(abort_code=2,location=soulidity_market::market)]
fun collection_sale_quote_is_bound_to_actual_buyer(){let(mut t,lid,_)=list_member(normal());t.sc.next_tx(@0xe);let mut l:market::Listing<Soul,USD> = t.sc.take_shared_by_id(lid);wrong_buyer_member_quote(&mut t,&mut l);test_scenario::return_shared(l);t.sc.next_tx(@0xb);end_t(t)}

#[test]
fun whole_member_sale_requotes_current_right_holder_pays_all_four_recipients_and_clears_grants() {
    let(mut t,lid,root)=list_member(normal());transfer_right(&mut t);t.sc.next_tx(@0xe);let mut l:market::Listing<Soul,USD> = t.sc.take_shared_by_id(lid);let snapshot=collection::snapshot_hash(&t.c);buy_member(&mut t,&mut l,snapshot);test_scenario::return_shared(l);t.sc.next_tx(@0xe);let s:Soul=t.sc.take_from_sender_by_id(root);assert!(soul::creator(&s)==@0xb && soul::collection_id(&s)==option::some(object::id(&t.c)) && soul::generation(&s)==1 && soul::grant_count(&s)==0 && soul::bound_count(&s)==1 && soul::binding(&s,b"bound").is_none() && soul::free_id(&soul::binding(&s,b"free").destroy_some()).is_some(),0);t.sc.return_to_sender(s);
    t.sc.next_tx(@0xc);let c:Coin<USD> = t.sc.take_from_sender();assert!(coin::value(&c)==21,1);t.sc.return_to_sender(c);t.sc.next_tx(@0xa);let c:Coin<USD> = t.sc.take_from_sender();assert!(coin::value(&c)==6,2);t.sc.return_to_sender(c);t.sc.next_tx(@0xb);let total=sum_coins(&t.sc);assert!(total==207,3);t.sc.next_tx(@0xf);assert!(sum_coins(&t.sc)==0 && soulidity_foundation::revenue::balance(economics::income(&t.cfg))==11,4);t.sc.next_tx(@0xb);end_t(t)
}

#[test]
#[expected_failure(abort_code=2,location=soulidity_market::market)]
fun stale_collection_recipient_snapshot_cannot_settle_member_sale(){let(mut t,lid,_)=list_member(normal());let old=collection::snapshot_hash(&t.c);transfer_right(&mut t);t.sc.next_tx(@0xe);let mut l:market::Listing<Soul,USD> = t.sc.take_shared_by_id(lid);buy_member(&mut t,&mut l,old);test_scenario::return_shared(l);t.sc.next_tx(@0xb);end_t(t)}

#[test]
#[expected_failure(abort_code=4,location=soulidity_market::market)]
fun ordinary_buy_entry_cannot_bypass_collection_fees(){let(mut t,lid,_)=list_member(normal());t.sc.next_tx(@0xe);let mut l:market::Listing<Soul,USD> = t.sc.take_shared_by_id(lid);plain_buy(&mut t,&mut l);test_scenario::return_shared(l);t.sc.next_tx(@0xb);end_t(t)}

#[test]
#[expected_failure(abort_code=1,location=soulidity_maker_terms::maker_resale)]
fun collection_valid_rate_can_still_exceed_combined_soul_fee(){let(t,_,_)=list_member(setup(9000,true,option::none(),option::none(),false));end_t(t)}

#[test,expected_failure(abort_code=3,location=soulidity_market::market)]
fun unbound_soul_cannot_claim_collection_membership(){
    let F{mut sc,c,k,a,cfg,factory,policy,clock,s,spare}=normal();let h=soul::manifest_hash(&s);
    market::list_soul_with_collection(s,&c,&cfg,101,1000,0,h,0,&clock,sc.ctx());
    test_scenario::return_shared(c);test_scenario::return_shared(k);test_scenario::return_shared(cfg);test_scenario::return_shared(factory);test_scenario::return_shared(policy);sc.return_to_sender(a);sc.return_to_sender(spare);clock::destroy_for_testing(clock);sc.end();
}
