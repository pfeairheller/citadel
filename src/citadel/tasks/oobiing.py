from hio.base import doing
from keri.app import oobiing


class OOBILoader(doing.DoDoer):
    def __init__(self, hby):
        self.hby = hby
        self.oc = self.hby.db.oobis.cntAll()

        print(f"\nLoading {self.oc} OOBIs...")
        doers = oobiing.Oobiery(hby=self.hby).doers
        super(OOBILoader, self).__init__(doers=doers)
        
    def recur(self, tyme, deeds=None):
        if self.oc > self.hby.db.roobi.cntAll():
            return super(OOBILoader, self).recur(tyme, deeds)

        for (oobi,), obr in self.hby.db.roobi.getItemIter():
            if obr.state in (oobiing.Result.resolved,):
                print(oobi, "succeeded")
            if obr in (oobiing.Result.failed,):
                print(oobi, "failed")

        self.remove(self.doers)
        return super(OOBILoader, self).recur(tyme, deeds)


class OOBIAuther(doing.DoDoer):
    def __init__(self, hby):
        self.hby = hby
        self.wc = [oobi for (oobi,), _ in self.hby.db.woobi.getItemIter()]

        if len(self.wc) == 0:
            doers = []
        else:
            print(f"\nAuthenticating Well-Knowns...")
            authn = oobiing.Authenticator(hby=self.hby)
            doers = authn.doers

        super(OOBIAuther, self).__init__(doers=doers)

    def recur(self, tyme, deeds=None):
        cap = []
        for (_,), wk in self.hby.db.wkas.getItemIter(keys=b''):
            cap.append(wk.url)

        if set(self.wc) & set(cap) != set(self.wc):
            return False

        self.remove(self.doers)
        return super(OOBIAuther, self).recur(tyme, deeds)
