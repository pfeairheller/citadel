import asyncio
from ordered_set import OrderedSet as oset

from hio.base import tyming, doing
from hio.help import decking
from keri.app import delegating, grouping, connecting, oobiing, agenting, forwarding, storing, habbing, signaling, \
    notifying, challenging, querying, indirecting
from keri.core import routing, eventing, coring
from keri.peer import exchanging
from keri.vc import protocoling
from keri.vdr import verifying, credentialing
from keri.vdr.eventing import Tevery


class Agent(doing.DoDoer):
    """

    The top level object and DoDoer representing a Habery for a remote controller and all associated processing

    """

    def __init__(self, app, hby, rgy):
        self.hby = hby
        self.rgy = rgy

        self.swain = delegating.Sealer(hby=hby)
        self.counselor = grouping.Counselor(hby=hby, swain=self.swain)
        self.org = connecting.Organizer(hby=hby)

        oobiery = oobiing.Oobiery(hby=hby)

        self.cues = decking.Deck()
        self.groups = decking.Deck()
        self.anchors = decking.Deck()
        self.witners = decking.Deck()
        self.queries = decking.Deck()
        self.exchanges = decking.Deck()

        receiptor = agenting.Receiptor(hby=hby)
        self.postman = forwarding.Poster(hby=hby)
        self.witPub = agenting.WitnessPublisher(hby=self.hby)
        self.witDoer = agenting.WitnessReceiptor(hby=self.hby)

        self.rep = storing.Respondant(hby=hby, cues=self.cues,
                                      mbx=storing.Mailboxer(name=self.hby.name, temp=self.hby.temp))

        doers = [habbing.HaberyDoer(habery=hby), receiptor, self.postman, self.witPub, self.rep, self.swain,
                 self.counselor, self.witDoer, *oobiery.doers]

        signaler = signaling.Signaler()
        self.notifier = notifying.Notifier(hby=hby, signaler=signaler)
        self.mux = grouping.Multiplexor(hby=hby, notifier=self.notifier)

        # Initialize all the credential processors
        self.verifier = verifying.Verifier(hby=hby, reger=rgy.reger)
        self.registrar = credentialing.Registrar(hby=hby, rgy=rgy, counselor=self.counselor)
        self.credentialer = credentialing.Credentialer(hby=self.hby, rgy=self.rgy, registrar=self.registrar,
                                                       verifier=self.verifier)

        challengeHandler = challenging.ChallengeHandler(db=hby.db, signaler=signaler)

        handlers = [challengeHandler]
        self.exc = exchanging.Exchanger(hby=hby, handlers=handlers)
        grouping.loadHandlers(exc=self.exc, mux=self.mux)
        protocoling.loadHandlers(hby=self.hby, exc=self.exc, notifier=self.notifier)

        self.rvy = routing.Revery(db=hby.db, cues=self.cues)
        self.kvy = eventing.Kevery(db=hby.db,
                                   lax=True,
                                   local=False,
                                   rvy=self.rvy,
                                   cues=self.cues)
        self.kvy.registerReplyRoutes(router=self.rvy.rtr)

        self.tvy = Tevery(reger=self.verifier.reger,
                          db=hby.db,
                          local=False,
                          cues=self.cues)

        self.tvy.registerReplyRoutes(router=self.rvy.rtr)
        self.mbx = indirecting.MailboxDirector(
            hby=self.hby,
            topics=['/receipt', '/multisig', '/replay', "/delegate", "/credential"],
            exc=self.exc,
            kvy=self.kvy,
            tvy=self.tvy,
            rvy=self.rvy,
            verifier=self.verifier)

        doers.extend([
            self.mbx,
            Querier(hby=hby, kvy=self.kvy, queries=self.queries),
            Witnesser(app=app, receiptor=receiptor, witners=self.witners),
            Delegator(hby=self.hby, swain=self.swain, anchors=self.anchors),
            ExchangeSender(hby=hby, exc=self.exc, postman=self.postman, exchanges=self.exchanges),
            GroupRequester(app=app, hby=hby, counselor=self.counselor, groups=self.groups)
        ])

        super(Agent, self).__init__(doers=doers, always=True)


class Witnesser(doing.Doer):

    def __init__(self, app, receiptor, witners):
        self.app = app
        self.receiptor = receiptor
        self.witners = witners
        self.cues = decking.Deck()
        asyncio.create_task(self.processCues())

        super(Witnesser, self).__init__()

    def recur(self, tyme=None):
        while True:
            if self.witners:
                msg = self.witners.popleft()
                serder = msg["serder"]

                # If we are a rotation event, may need to catch new witnesses up to current key state
                if serder.ked['t'] in (coring.Ilks.rot, coring.Ilks.drt):
                    adds = serder.ked["ba"]
                    for wit in adds:
                        yield from self.receiptor.catchup(serder.pre, wit)

                yield from self.receiptor.receipt(serder.pre, serder.sn)
                self.cues.push(msg)

            yield self.tock

    async def processCues(self):
        while True:
            if self.cues:
                cue = self.cues.popleft()
                serder = cue['serder']
                await self.app.snack(f"Witness receipts received for {serder.pre}.")

            await asyncio.sleep(1.0)


class Delegator(doing.Doer):

    def __init__(self, hby, swain, anchors):
        self.hby = hby
        self.swain = swain
        self.anchors = anchors
        super(Delegator, self).__init__()

    def recur(self, tyme=None):
        if self.anchors:
            msg = self.anchors.popleft()
            sn = msg["sn"] if "sn" in msg else None

            proxy = msg["proxy"]
            phab = self.hby.habByName(proxy)

            self.swain.delegation(pre=msg["pre"], sn=sn, proxy=phab)

        return False


class ExchangeSender(doing.Doer):

    def __init__(self, hby, postman, exc, exchanges):
        self.hby = hby
        self.postman = postman
        self.exc = exc
        self.exchanges = exchanges
        super(ExchangeSender, self).__init__()

    def recur(self, tyme):
        if self.exchanges:
            msg = self.exchanges.popleft()
            said = msg['said']
            if not self.exc.complete(said=said):
                self.exchanges.append(msg)
                return False

            serder, pathed = exchanging.cloneMessage(self.hby, said)

            src = msg["src"]
            pre = msg["pre"]
            rec = msg["rec"]
            topic = msg['topic']
            hab = self.hby.habs[pre]
            if self.exc.lead(hab, said=said):
                atc = exchanging.serializeMessage(self.hby, said)
                del atc[:serder.size]
                for recp in rec:
                    self.postman.send(src=src,
                                      dest=recp,
                                      topic=topic,
                                      serder=serder,
                                      attachment=atc)


class GroupRequester(doing.Doer):

    def __init__(self, app, hby, counselor, groups):
        self.app = app
        self.hby = hby
        self.counselor = counselor
        self.groups = groups
        self.cues = decking.Deck()
        asyncio.create_task(self.processCues())

        super(GroupRequester, self).__init__()

    def recur(self, tyme):
        """ Checks cue for group proceccing requests and processes any with Counselor """
        if self.groups:
            msg = self.groups.popleft()
            serder = msg["serder"]

            ghab = self.hby.habs[serder.pre]

            icp = ghab.makeOwnInception(allowPartiallySigned=True)

            # Create a notification EXN message to send to the other agents
            exn, ims = grouping.multisigInceptExn(ghab.mhab,
                                                  smids=ghab.smids,
                                                  rmids=ghab.rmids,
                                                  icp=icp)
            others = list(oset(ghab.smids + (ghab.rmids or [])))

            others.remove(ghab.mhab.pre)

            for recpt in others:  # this goes to other participants only as a signaling mechanism
                self.app.agent.postman.send(src=ghab.mhab.pre,
                                            dest=recpt,
                                            topic="multisig",
                                            serder=exn,
                                            attachment=ims)

            print(f"Group identifier inception initialized for {ghab.pre}")
            prefixer = coring.Prefixer(qb64=serder.pre)
            seqner = coring.Seqner(sn=serder.sn)
            saider = coring.Saider(qb64=serder.said)
            self.counselor.start(ghab=ghab, prefixer=prefixer, seqner=seqner, saider=saider)
            self.cues.push(dict(serder=serder))

        return False

    async def processCues(self):
        while True:
            if self.cues:
                cue = self.cues.popleft()
                serder = cue['serder']
                if self.counselor.complete(said=serder.said):
                    await self.app.snack(f"Multisig AID complete for {serder.pre}.")
                else:
                    self.cues.push(cue)

            await asyncio.sleep(1.0)


class Querier(doing.DoDoer):

    def __init__(self, hby, queries, kvy):
        self.hby = hby
        self.queries = queries
        self.kvy = kvy

        super(Querier, self).__init__(always=True)

    def recur(self, tyme, deeds=None):
        """ Processes query reqests submitting any on the cue"""
        if self.queries:
            msg = self.queries.popleft()
            src = msg["src"]
            pre = msg["pre"]

            hab = self.hby.habByName(src)

            if "sn" in msg:
                seqNoDo = querying.SeqNoQuerier(hby=self.hby, hab=hab, pre=pre, sn=msg["sn"])
                self.extend([seqNoDo])
            elif "anchor" in msg:
                pass
            else:
                qryDo = querying.QueryDoer(hby=self.hby, hab=hab, pre=pre, kvy=self.kvy)
                self.extend([qryDo])

        return super(Querier, self).recur(tyme, deeds)


def runController(app, hby, rgy, expire=0.0):
    agent = Agent(app=app, hby=hby, rgy=rgy)
    doers = [agent]

    tock = 0.03125
    doist = doing.Doist(doers=doers, limit=expire, tock=tock, real=True)
    htask = HioTask(doist=doist)

    asyncio.create_task(htask.run())

    return agent


class HioTask:

    def __init__(self, doist):
        self.doist = doist

    async def run(self, limit=None, tyme=None):
        self.doist.done = False

        if limit is not None:  # time limt for running if any. useful in test
            self.doist.limit = abs(float(limit))

        if tyme is not None:  # re-initialize starting tyme
            self.doist.tyme = tyme

        try:  # always clean up resources upon exception
            self.doist.enter()  # runs enter context on each doer

            tymer = tyming.Tymer(tymth=self.doist.tymen(), duration=self.doist.limit)
            self.doist.timer.start()

            while True:  # until doers complete or exception or keyboardInterrupt
                try:
                    self.doist.recur()  # increments .tyme runs recur context

                    if self.doist.real:  # wait for real time to expire
                        while not self.doist.timer.expired:
                            await asyncio.sleep(max(0.0, self.doist.timer.remaining))
                        self.doist.timer.restart()  # no time lost

                    if not self.doist.deeds:  # no deeds
                        self.doist.done = True
                        break  # break out of forever loop

                    if self.doist.limit and tymer.expired:  # reached time limit
                        break  # break out of forever loop

                except KeyboardInterrupt:  # use CNTL-C to shutdown from shell
                    break

                except SystemExit:  # Forced shutdown of process
                    raise

                except Exception:  # Unknown exception
                    raise

        finally:  # finally clause always runs regardless of exception or not.
            self.doist.exit()  # force close remaining deeds throws GeneratorExit
