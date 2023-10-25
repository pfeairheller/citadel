from hio.base import doing
from keri.app import habbing, delegating, forwarding, indirecting, agenting
from keri.core import coring


class Incepter(doing.DoDoer):
    def __init__(self, hby, hab, proxy=None):
        self.hby = hby
        self.hab = hab
        self.proxy = proxy
        self.swain = delegating.Boatswain(hby=hby)
        self.postman = forwarding.Poster(hby=hby)
        self.mbx = indirecting.MailboxDirector(hby=hby, topics=['/receipt', "/replay", "/reply"])
        self.receiptor = agenting.Receiptor(hby=self.hby)

        doers = [self.postman, self.mbx, self.swain, self.receiptor, doing.doify(self.inceptDo)]
        super(Incepter, self).__init__(doers=doers)

    def inceptDo(self, tymth, tock=0.0):
        # enter context
        self.wind(tymth)
        self.tock = tock
        _ = (yield self.tock)

        if self.hab.kever.delegator:
            self.swain.delegation(pre=self.hab.pre, sn=0, proxy=self.hby.habByName(self.proxy))
            print("Waiting for delegation approval...")
            while not self.swain.complete(self.hab.kever.prefixer, coring.Seqner(sn=self.hab.kever.sn)):
                yield self.tock

        elif self.hab.kever.wits:
            print("Waiting for witness receipts...")
            yield from self.receiptor.receipt(self.hab.pre, sn=0)

        if self.hab.kever.delegator:
            yield from self.postman.sendEvent(hab=self.hab, fn=self.hab.kever.sn)

        print(f'Prefix  {self.hab.pre}')
        for idx, verfer in enumerate(self.hab.kever.verfers):
            print(f'\tPublic key {idx + 1}:  {verfer.qb64}')
        print()

        toRemove = [self.mbx, self.swain, self.postman, self.receiptor]
        self.remove(toRemove)
