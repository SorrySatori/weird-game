/**
 * Czech intro scene text – vyprávění a dialogy z úvodní scény.
 * `opening`: titulky k úvodnímu záběru na Hymnar (posvátnou houbu boha Obazoby, ne boha samotného); `dialogues[].who` určuje, která postava v síni mluví.
 */
export default {
    intro: {
        opening: [
            'Hluboko pod zemí, daleko za hranicemi Horní Morkezely, roste Hymnar – posvátná houba boha Obazoby.',
            'Obazoba sám žádné tělo nemá. Je zdrojem veškerého života i veškeré hniloby, ideálem, kterého se nikdo nikdy nedotkl. Hymnar je jen jeho svatyně. Věřící ale tvrdí, že jeho podhoubím je slyšet celý svět.',
            'Té noci Hymnarovým podhoubím projelo zachvění. Volání o pomoc, jaké se ozve jednou za generaci. Možná za dvě.',
        ],
        dialogues: [
            { who: 'narrator', speaker: 'VYPRAVĚČ', text: 'V podzemním chrámu boha Obazoby zasedá Rada Nejvyššího Humenia.' },
            { who: 'varhun', speaker: 'ARCIKNĚZ VARHUN', text: 'Zachytili jsme nouzový signál myceliální sítí. Volání o pomoc.' },
            { who: 'tynri', speaker: 'ARCIKNĚZ TYNRI', text: 'Z povrchu. Z města Horní Morkezela.' },
            { who: 'varhun', speaker: 'ARCIKNĚZ VARHUN', text: 'Musíme odpovědět, i když nevíme, kdo volá.' },
            { who: 'rhull', speaker: 'ARCIKNĚZ RHULL', text: 'Měli bychom jít do Vaječné katedrály. Biskupka bude vědět víc – k jejím úkolům patřilo monitorovat, co se ve městě děje.' },
            { who: 'varhun', speaker: 'ARCIKNĚZ VARHUN', text: 'Přivolejte mistra Thaala, aby kráčel cestou mrtvých kořenů. Ať povstane houbový vyslanec.' },
            { who: 'tynri', speaker: 'ARCIKNĚZ TYNRI', text: 'Vyšetřovatel by to mohl být schopný, to ano. Ale mám dojem, že jeho učedník je... poněkud problematická osoba, řekněme.' },
            { who: 'rhull', speaker: 'ARCIKNĚZ RHULL', text: 'Je to... no, je to Thaalův učedník. Moc o něm nevím, ale vím, že není zrovna... nejbystřejší houba v lese.' },
            { who: 'rhull', speaker: 'ARCIKNĚZ RHULL', text: 'Alespoň jsme tentokrát schovali obřadní oleje.' },
            { who: 'tynri', speaker: 'ARCIKNĚZ TYNRI', text: 'A zamkli houbový archiv. Dvakrát.' },
            { who: 'varhun', speaker: 'ARCIKNĚZ VARHUN', text: 'Zavolejte mistra Thaala. Ať najde Biskupku Horní Morkezely a odhalí zdroj toho nouzového volání. Ten učedník je jeho starost. A pokud se nevrátí zpátky, taky dobrý. Vždycky mu můžeme najít nového.' },
        ],
        skipHint: 'ESC – přeskočit',
        transition: 'Po několika dnech cesty se před tebou konečně objeví město Horní Morkezela...',
    },
};
