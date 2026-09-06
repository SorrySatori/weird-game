# Dialog review — Master Thaal / Mistr Thaal  (EntryScene, úvod dema)

**Jak editovat:**
- Uprav jen text za `EN:` a `CZ:`. **Neměň** nadpisy `## [klíč]` ani klíče voleb `` `[klíč]` `` — podle nich to mapuju zpět.
- `\n\n` = odstavcový zlom, nech ho v textu.
- Hvězdičkové *poznámky* (gesta) klidně uprav jako text.
- Struktura (které volby kam vedou) je herní logika — needituj, jen texty. Když chceš přidat/ubrat volbu nebo změnit tok, napiš to slovně do komentáře.
- Až budeš hotov, pošli soubor zpět a já to zapíšu do `scenes/EntryScene.js` + `lang/cs/dialogs/EntryScene.js`.

**Mluvčí:** EN `Master Thaal` · CZ `Mistr Thaal`

**Automatická odchozí volba** (přidává se sama do většiny „tématických" stavů — edituj ji tady jednou):
- `[ill_be_on_my_way_injected]`
  - EN: I'll be on my way.
  - CZ: Už půjdu.

---

## [main]
EN: Ah, my apprentice, there you are! *sigh* I've been waiting for you. Listen carefully, for I have an important task that requires... well, someone of your particular talents.
CZ: Ach, můj učedníku, tady jsi! *povzdech* Čekal jsem na tebe. Poslouchej pozorně, mám pro tebe důležitý úkol, který vyžaduje... někoho s tvými zvláštními schopnostmi.

Options:
- `[what_task_master]`
  - EN: What task, Master?
  - CZ: Jaký úkol, Mistře?
- `[why_cant_you_do_it_yourself]`
  - EN: Why can't you do it yourself?
  - CZ: Proč to nemůžete udělat sám?

## [hub]
EN: *He glances up, impatient to get back to his tankard.* Was there something else, apprentice?
CZ: *Zvedne pohled, netrpělivý, aby se vrátil ke svému džbánku.* Bylo ještě něco, učedníku?

Options:
- `[tell_me_more_about_the_city]`
  - EN: Tell me more about the city.
  - CZ: Řekněte mi víc o městě.
- `[who_are_the_gods]`
  - EN: Who are the gods here?
  - CZ: Kdo jsou zdejší bohové?
- `[tell_me_more_about_city_locations]`
  - EN: Tell me about the city's locations.
  - CZ: Řekněte mi o místech ve městě.
- `[do_you_have_any_advice_for_me]`
  - EN: Do you have any advice for me?
  - CZ: Máte pro mě nějakou radu?

## [task]
EN: You must find the Bishop at the Egg Cathedral. She might knows about the distress call we have received from this city via myceliar network. The Bishop should be present at the Egg Cathedral.
CZ: Musíš najít Biskupku v Vaječné katedrále. Možná ví něco o nouzovém volání, které jsme přijali z tohoto města přes myceliární síť. Biskupka by měla být přítomna ve Vaječné katedrále.

Options:
- `[wait_do_you_mean_the_task_you_have_been_given_by_t]`
  - EN: Wait, do you mean the task you have been given by the Spore Council? The only reason we are here? Why can't we go see the Bishop together?
  - CZ: Počkejte, myslíte ten úkol, který jste dostal od Sporové rady? Jediný důvod, proč jsme tady? Proč nemůžeme jít za Biskupkou spolu?
- `[tell_me_more_about_the_city_first]`
  - EN: Tell me more about the city first
  - CZ: Nejdřív mi řekněte víc o městě

## [whyNot]
EN: *adjusts robe importantly* I am far too busy with... important research. Yes! Research into advanced mycological phenomena that your novice mind couldn't possibly comprehend. Besides, I have a... prior engagement at the Fermented Cap tavern. The Bishop specifically requested someone of your... particular level of experience.
CZ: *důležitě si upravuje hábit* Jsem příliš zaneprázdněn... důležitým výzkumem. Ano! Výzkumem pokročilých mykologických jevů, které by tvá začátečnická mysl nemohla pochopit. Kromě toho mám... předchozí závazek v hospodě U Kvašeného klobouku. Biskupka si výslovně vyžádala někoho s tvou... konkrétní úrovní zkušeností.

Options:
- `[youre_just_avoiding_work_arent_you]`
  - EN: You're just avoiding work, aren't you?
  - CZ: Vy se prostě jen vyhýbáte práci, že?
- `[what_should_i_tell_the_bishop_when_i_find_her]`
  - EN: What should I tell the Bishop when I find her?
  - CZ: Co mám říct Biskupce, až ji najdu?
- `[tell_me_more_about_the_city_first]`
  - EN: Tell me more about the city first
  - CZ: Nejdřív mi řekněte víc o městě

## [avoiding]
EN: *huffs indignantly* How dare you! I am conducting vital... spiritual communion with the fermented spirits. It's a sacred ritual that requires my full attention and several mugs of mushroom ale. Now, off you go! The Bishop awaits, and this is excellent training for you. Consider yourself fortunate!
CZ: *uraženě odfrkne* Jak se opovažuješ! Provádím životně důležité... duchovní obcování s kvašenými nápoji. Je to posvátný rituál, který vyžaduje mou plnou pozornost a několik džbánků houbového piva. A teď už běž! Biskupka čeká a tohle je pro tebe vynikající trénink. Považuj se za šťastlivce!

Options:
- `[what_should_i_tell_the_bishop_when_i_find_her]`
  - EN: What should I tell the Bishop when I find her?
  - CZ: Co mám říct Biskupce, až ji najdu?
- `[tell_me_more_about_the_city_first]`
  - EN: Tell me more about the city first
  - CZ: Nejdřív mi řekněte víc o městě
- `[master_i_have_heard_that_upper_morkezela_is_called]`
  - EN: Master, I have heard that Upper Morkezela is called the Dead gods city. Could you tell me more?
  - CZ: Mistře, slyšel jsem, že Horní Morkezele se říká město mrtvých bohů. Mohl byste mi říct víc?

## [tellBishop]
EN: Tell her you're my apprentice, sent to assist with the spore disturbance investigation. She'll know what to do. And remember to represent the fungal clergy with dignity! No embarrassing me this time. Now, was there anything else you needed to know before you go?
CZ: Řekni jí, že jsi můj učedník, vyslaný na pomoc s vyšetřováním sporových poruch. Bude vědět, co dělat. A nezapomeň reprezentovat houbové duchovenstvo důstojně! Žádné trapasy, tentokrát. A teď, potřeboval jsi ještě něco vědět, než vyrazíš?

Options:
- `[tell_me_more_about_the_city]`
  - EN: Tell me more about the city
  - CZ: Řekněte mi víc o městě
- `[who_are_the_gods]`
  - EN: Who are the gods?
  - CZ: Kdo jsou ti bohové?
- `[ill_be_on_my_way]`
  - EN: I'll be on my way
  - CZ: Vyrazím na cestu

## [farewell]
EN: Excellent! The Egg Cathedral is just to the east. And if anyone asks, tell them I'm engaged in VERY important spiritual communion that cannot be disturbed.\n\nBut heed a few things before you go, apprentice. Your actions have consequences — some will make the city grow, others make it rot and decay, and the city will look and treat you accordingly. And mind the spores up here: you have only ever breathed the thick, obedient air of Obazoba's temple, and under open sky they are a different beast. And should the city's walking, talking fungus ever take an interest in you — the symbionts, that you've only read about — best you know a little first. Well? Anything to ask before you go?
CZ: Výborně! Vaječná katedrála je hned na východ. A kdyby se někdo ptal, řekni, že se věnuji VELMI důležitému duchovnímu obcování, které nesmí být rušeno.\n\nAle než půjdeš, dej pozor na pár věcí, učedníku. Tvé činy mají následky — některé nechají město růst, jiné hnít a chátrat, a město podle toho bude vypadat i jednat s tebou. A dávej pozor na spóry tady nahoře: dosud jsi dýchal jen hustý, poslušný vzduch Obazobova chrámu, a pod širým nebem jsou to úplně jiná zvěř. A kdyby o tebe někdy projevila zájem chodící, mluvící houba tohohle města — symbionti, o kterých jsi jen četl — bude lepší, když o nich něco víš. Tak co? Chceš se na něco zeptat, než vyrazíš?

Options:
- `[wait_tell_me_more_about_the_growth_and_decay]`
  - EN: Tell me more about the growth and decay.
  - CZ: Řekněte mi víc o růstu a rozkladu.
- `[the_spores_different_how]`
  - EN: The spores — a different beast how?
  - CZ: Spóry — jak jako jiná zvěř?
- `[the_symbionts_tell_me_more]`
  - EN: The symbionts. Tell me more.
  - CZ: Symbionti. Řekněte mi víc.
- `[glory_to_the_eternal_mushroom]`
  - EN: Thank you, I have nothing more to ask. Glory to the Eternal Mushroom...
  - CZ: Sláva Věčné houbě...

## [growthDecay]
EN: Well, the terms speak for themselves, aren't they? Growth is when the city is growing, when it is thriving and prospering. Decay is when the city is decaying, when the rot has the upper hand. As you know, my apprentice, Obazoba is master of both principles. Therefore, they are equal, none of them is better than the other. But of course, not every citizen here will share this opinion. Some of them will prefer growth, some will prefer decay. Some will prefer balance between them. Some will prefer none of them. It's up to you to find out, but be careful.
CZ: No, ty pojmy mluví samy za sebe, ne? Růst je, když město roste, když prosperuje a vzkvétá. Rozklad je, když město chátrá, když má navrch hniloba. Jak víš, můj učedníku, Obazoba je pánem obou principů. Proto jsou si rovny, žádný není lepší než druhý. Ale samozřejmě, ne každý občan tady bude sdílet tento názor. Někteří budou preferovat růst, jiní rozklad. Někteří budou preferovat rovnováhu mezi nimi. Někteří nebudou preferovat ani jedno. Je na tobě, abys to zjistil, ale buď opatrný.

Options:
- `[and_these_spores]`
  - EN: And the spores you mentioned?
  - CZ: A ty spóry, co jste zmínil?
- `[the_symbionts_tell_me_more]`
  - EN: What about the symbionts?
  - CZ: A co ti symbionti?
- `[glory_to_the_eternal_mushroom]`
  - EN: Thank you, I have nothing more to ask. Glory to the Eternal Mushroom...
  - CZ: Sláva Věčné houbě...

## [tutorialOffer]
EN: *He is already half-turned toward the tavern when he stops, one finger raised.* Wait! You should know that a master priest of my rank commands one further superpower: meta-narrative awareness — deeply useful for explaining how this world actually works. So, before I go: shall I show you how to use your gear? Your diary, the map, that sort of thing?
CZ: *Už je napůl otočený k hospodě, když se zastaví a zvedne prst.* Počkej! Měl bys vědět, že mistr kněz mého řádu ovládá ještě jednu superschopnost: meta-narativní vědomí — nesmírně užitečné pro vysvětlování, jak tenhle svět vlastně funguje. Takže než půjdu: mám ti ukázat, jak zacházet s výbavou? Deník, mapa a tak podobně?

Options:
- `[tutorial_yes]`
  - EN: Yes please, Master.
  - CZ: Ano prosím, Mistře.
- `[tutorial_no]`
  - EN: No need. Objectively, the best games were made in 1997 — and we did just fine without tutorials back then.
  - CZ: Netřeba. Nejlepší hry objektivně vznikly v roce 1997 — a tenkrát jsme se bez tutoriálů taky obešli.

## [close]
EN: *waves dismissively while eyeing the path to the tavern*
CZ: *odmítavě mávne rukou a pokukuje po cestě k hospodě*

(žádné volby — konec větve)

## [city]
EN: Upper Morkezela... it breathes with ancient spores. The buildings grow like mushrooms in the dark, their patterns shifting when no one watches. Some say the entire city is a graveyard of forgotten gods from many spheres. Each time people cease to believe in some god, it grows. The dying gods bring streets, building and forgotten culture with them. They don't want to be alone in the void, afterlife or whatever there is for them after they die, you know. 
CZ: Horní Morkezela... dýchá starodávnými sporami. Budovy rostou jako houby ve tmě, jejich vzory se mění, když se nikdo nedívá. Někteří říkají, že celé město je hřbitov zapomenutých bohů z mnoha sfér. Pokaždé, když lidé přestanou věřit v nějakého boha, město roste. Umírající bohové s sebou přinášejí ulice, budovy a zapomenutou kulturu. Nechtějí být sami v prázdnotě, posmrtném životě nebo čemkoliv, co je čeká po smrti, víš.

Options:
- `[ask_about_the_gods]`
  - EN: Ask about the gods
  - CZ: Zeptejte se na bohy
- `[do_you_have_any_advice_for_me]`
  - EN: Do you have any advice for me?
  - CZ: Máte pro mě nějakou radu?
- `[tell_me_more_about_city_locations]`
  - EN: Tell me more about city locations.
  - CZ: Řekněte mi víc o místech ve městě.
- `[return_to_previous_topic]`
  - EN: Return to previous topic
  - CZ: Zpět k předchozímu tématu

## [spores]
EN: Down in the temple the spores lie thick and close and obedient — the god's own breath, pooled in the dark. That is all you have ever known of them. But out here, under open sky, they thin and scatter and get into everything. They drift the streets; they carry the city's whispering along the mycelium — that is how the distress call reached the Council at all, riding the spores through the myceliar network. Your temple-lungs will find it strange awhile. And mind: the spores gather in you over time, a quiet pressure behind the eyes — and there are things in this city that feed on exactly that.
CZ: Dole v chrámu leží spóry husté, blízké a poslušné — vlastní dech boha, nahromaděný ve tmě. Nic jiného jsi nepoznal. Ale tady venku, pod širým nebem, řídnou, rozptylují se a lezou úplně všude. Vanou ulicemi; nesou šepot města po myceliu — právě tak vůbec dorazilo nouzové volání k Radě, na spórách, myceliární sítí. Tvým chrámovým plícím to chvíli přijde divné. A dej pozor: spóry se v tobě časem hromadí, tichý tlak za očima — a v tomhle městě jsou věci, které se právě tím živí.

Options:
- `[things_that_feed_symbionts]`
  - EN: Things that feed on it? The symbionts?
  - CZ: Věci, co se tím živí? Symbionti?
- `[return_to_previous_topic]`
  - EN: Return to previous topic
  - CZ: Zpět k předchozímu tématu

## [symbionts]
EN: Heard of them in the cloister archives, no doubt — and never seen one bonded. You carry none; you'd walk differently if you did. A symbiont is a living thing you invite into your own flesh, apprentice: bonded to you, each with its own voice and its own gift — one reads the thought folded behind a face, one the last words of the dead, one the seam in a wall that only pretends to be solid. This city keeps them in its odd corners. Should one offer itself, and you prove worthy — or foolish enough — you may take it in. But mind the balance: some wax strong in Growth and fall silent in Decay; others the reverse. Tip the city too far and your new voice may simply stop speaking. Enough! I have communion to attend.
CZ: O těch jsi jistě četl v klášterních archivech — a nikdy žádného spojeného neviděl. Sám žádného nenosíš; jinak by ses hýbal jinak. Symbiont je živá věc, kterou zveš do vlastního masa, učedníku: spojená s tebou, každý má svůj hlas a svůj dar — jeden čte myšlenku složenou za tváří, jiný poslední slova mrtvých, další šev ve zdi, která jen předstírá, že je pevná. Tohle město je chová ve svých podivných koutech. Kdyby se ti některý nabídl a ty se ukázal hoden — nebo dost pošetilý — můžeš si ho vzít do sebe. Ale dej pozor na rovnováhu: někteří sílí v Růstu a umlkají v Rozkladu, jiní naopak. Nakloň město příliš a tvůj nový hlas možná prostě přestane mluvit. Dost! Čeká mě obcování.

Options:
- `[and_these_spores]`
  - EN: And these spores you mentioned?
  - CZ: A ty spóry, co jste zmínil?
- `[tell_me_again_growth_decay]`
  - EN: Tell me again about growth and decay.
  - CZ: Řekněte mi znovu o růstu a rozkladu.
- `[return_to_previous_topic]`
  - EN: Return to previous topic
  - CZ: Zpět k předchozímu tématu

## [advice]
EN: Remember, all your actions have consequences. Some of them will cause the city to grow, some will cause it to rot and decay. Your action can change the city and its future. They can change how the city will look and how its inhabitants will live and react to you.
CZ: Pamatuj, všechny tvé činy mají následky. Některé způsobí, že město poroste, jiné že bude hnít a chátrat. Tvé jednání může změnit město a jeho budoucnost. Může změnit, jak město bude vypadat a jak jeho obyvatelé budou žít a reagovat na tebe.

Options:
- `[ask_about_the_gods]`
  - EN: Ask about the gods
  - CZ: Zeptejte se na bohy
- `[tell_me_more_about_city_locations]`
  - EN: Tell me more about city locations.
  - CZ: Řekněte mi víc o místech ve městě.
- `[return_to_previous_topic]`
  - EN: Return to previous topic
  - CZ: Zpět k předchozímu tématu

## [gods]
EN: You know, or you should know, that there is only one real god. Obozoba, the Ur-mushroom, the one who created the world and all life and death in it. The other gods are just illusions... but yeah, this is a city where gods are going to die. See, not all gods live forever.
CZ: Víš, nebo bys měl vědět, že existuje jen jeden skutečný bůh. Obazoba, Pra-houba, ten, kdo stvořil svět a veškerý život i smrt v něm. Ostatní bohové jsou jen iluze... ale jo, tohle je město, kam bohové přicházejí umírat. Víš, ne všichni bohové žijí věčně.

Options:
- `[ask_about_the_city]`
  - EN: Ask about the city
  - CZ: Zeptejte se na město
- `[where_can_i_learn_more_about_the_gods]`
  - EN: Where can I learn more about the gods?
  - CZ: Kde se mohu dozvědět víc o bozích?
- `[return_to_previous_topic]`
  - EN: Return to previous topic
  - CZ: Zpět k předchozímu tématu

## [priests]
EN: Go to the Egg Cathedral and talk to some of the priests there. They are always happy to chat. I mean, talk to our priest or the Bishop. Don't talk to the other gods' priests. I mean, the false gods' priests. The false priests. Ehm. You get me.
CZ: Jdi do Vaječné katedrály a promluv si s některými kněžími tam. Vždy rádi pokecají. Tedy, mluv s naším knězem nebo Biskupkou. Nemluv s kněžími ostatních bohů. Tedy, falešných bohů. Faleš- kněžími. Ehm. Chápeš mě.

Options:
- `[could_you_tell_me_more_about_the_egg_catedral]`
  - EN: Could you tell me more about the Egg Cathedral?
  - CZ: Mohl byste mi říct víc o Vaječné katedrále?
- `[return_to_previous_topic]`
  - EN: Return to previous topic
  - CZ: Zpět k předchozímu tématu

## [eggCatedral]
EN: The Egg Cathedral is, well, a huge cathedral that is hatching from a gigantic egg. A massive, shell-grown structure inhabited by fungal clergy, flickering with bio-luminescent scripture... They don't know which religion the cathedral belongs to. So all major churches send their priests just to be sure. They wait for the signs they hope for, but the cathedral is still hatching...
CZ: Vaječná katedrála je, no, obrovská katedrála, která se líhne z gigantického vejce. Masivní stavba porostlá skořápkou, obývaná houbovým duchovenstvem, mihotající se bioluminiscenčním písmem... Nevědí, ke kterému náboženství katedrála patří. Tak všechny hlavní církve posílají svého kněze, jen pro jistotu. Čekají na znamení, v která doufají, ale katedrála se stále líhne...

Options:
- `[return_to_previous_topic]`
  - EN: Return to previous topic
  - CZ: Zpět k předchozímu tématu

## [locations]
EN: The city has many locations, but the most significant ones are the Yolk Sea, Shed 521, Scraper 1140, Voxmarket, and the Stomach Clock. Which one interests you?
CZ: Město má mnoho lokací, ale ty nejvýznamnější jsou Žloutkové moře, Kůlna 521, Škrabák 1140, Voxmarket a Žaludeční hodiny. Která tě zajímá?

Options:
- `[shed_512]`
  - EN: Shed 521
  - CZ: Kůlna 521
- `[yolk_sea]`
  - EN: Yolk Sea
  - CZ: Žloutkové moře
- `[scraper_1140]`
  - EN: Scraper 1140
  - CZ: Škrabák 1140
- `[voxmarket]`
  - EN: Voxmarket
  - CZ: Voxmarket
- `[stomach_clock]`
  - EN: Stomach Clock
  - CZ: Žaludeční hodiny
- `[return_to_previous_topic]`
  - EN: Return to previous topic
  - CZ: Zpět k předchozímu tématu

## [shed512]
EN: Shed 521, also known as the Bureau of Shapes. A twisted bureaucracy in an old shipping yard turned into an ever-expanding cubicle labyrinth. People come here to register their current form or apply for bodily adjustments. You can find it right next to the Voxmarket
CZ: Kůlna 521, také známá jako Úřad tvarů. Zkroucená byrokracie ve starém překladišti přeměněná v neustále se rozrůstající labyrint kancelářských boxů. Lidé sem chodí registrovat svou současnou podobu nebo žádat o tělesné úpravy. Najdeš ji hned vedle Voxmarketu.

Options:
- `[what_is_the_egg_cathedral]`
  - EN: What is the Egg Cathedral?
  - CZ: Co je Vaječná katedrála?
- `[what_is_the_yolk_sea]`
  - EN: What is the Yolk Sea?
  - CZ: Co je Žloutkové moře?
- `[what_is_the_scraper_1140]`
  - EN: What is the Scraper 1140
  - CZ: Co je Škrabák 1140?
- `[what_is_the_voxmarket]`
  - EN: What is the Voxmarket?
  - CZ: Co je Voxmarket?
- `[what_is_the_stomach_clock]`
  - EN: What is the Stomach Clock?
  - CZ: Co jsou Žaludeční hodiny?
- `[return_to_previous_topic]`
  - EN: Return to previous topic
  - CZ: Zpět k předchozímu tématu

## [yolkSea]
EN: The Yolk Sea is a glowing, sentient ocean of living yolk. Boats float like seeds, and whispers rise from its depths.
CZ: Žloutkové moře je zářící, vnímající oceán živého žloutku. Lodě plují jako semena a z hlubin stoupají šepoty.

Options:
- `[what_is_the_shed_512]`
  - EN: What is the Shed 521?
  - CZ: Co je Kůlna 521?
- `[what_is_the_scraper_1140]`
  - EN: What is the Scraper 1140
  - CZ: Co je Škrabák 1140?
- `[what_is_the_voxmarket]`
  - EN: What is the Voxmarket?
  - CZ: Co je Voxmarket?
- `[what_is_the_stomach_clock]`
  - EN: What is the Stomach Clock?
  - CZ: Co jsou Žaludeční hodiny?
- `[return_to_previous_topic]`
  - EN: Return to previous topic
  - CZ: Zpět k předchozímu tématu

## [scraper1140]
EN: It's a crooked skyscraper retrofitted into a vertical slum. Each floor houses a different caste, age, or species. I'm afraid I don't know much about it, but I would be careful around this place
CZ: Je to zkřivený mrakodrap přestavěný na vertikální slum. Každé patro obývá jiná kasta, věk nebo druh. Bohužel o tom moc nevím, ale na tomhle místě bych si dával pozor.

Options:
- `[what_is_the_shed_512]`
  - EN: What is the Shed 521?
  - CZ: Co je Kůlna 521?
- `[what_is_the_scraper_1140]`
  - EN: What is the Scraper 1140
  - CZ: Co je Škrabák 1140?
- `[what_is_the_stomach_clock]`
  - EN: What is the Stomach Clock?
  - CZ: Co jsou Žaludeční hodiny?
- `[return_to_previous_topic]`
  - EN: Return to previous topic
  - CZ: Zpět k předchozímu tématu

## [voxmarket]
EN: The Voxmarket is a bustling marketplace... audio bazaar where recorded voices, sounds, and thoughts are sold. Stalls display silent conversation loops. You can buy the sound of someone’s first heartbreak or a scream from before fire existed. I have heard that also black market thrives here.
CZ: Voxmarket je rušný tržiště... zvukový bazar, kde se prodávají nahrané hlasy, zvuky a myšlenky. Stánky vystavují tiché smyčky konverzací. Můžeš si koupit zvuk něčího prvního zlomeného srdce nebo výkřik z doby před existencí ohně. Slyšel jsem, že tu také kvete černý trh.

Options:
- `[what_is_the_shed_512]`
  - EN: What is the Shed 521?
  - CZ: Co je Kůlna 521?
- `[what_is_the_scraper_1140]`
  - EN: What is the Scraper 1140
  - CZ: Co je Škrabák 1140?
- `[what_is_the_stomach_clock]`
  - EN: What is the Stomach Clock?
  - CZ: Co jsou Žaludeční hodiny?
- `[return_to_previous_topic]`
  - EN: Return to previous topic
  - CZ: Zpět k předchozímu tématu

## [stomachClock]
EN: The Stomach Clock is a biomechanical chamber shaped like a digestive clock. Time runs in loops; bile is sacred. You can see it at the townhall
CZ: Žaludeční hodiny jsou biomechanická komora ve tvaru trávicích hodin. Čas běží ve smyčkách; žluč je posvátná. Můžeš je vidět na radnici.

Options:
- `[what_is_the_shed_512]`
  - EN: What is the Shed 521?
  - CZ: Co je Kůlna 521?
- `[what_is_the_scraper_1140]`
  - EN: What is the Scraper 1140
  - CZ: Co je Škrabák 1140?
- `[what_is_the_voxmarket]`
  - EN: What is the Voxmarket?
  - CZ: Co je Voxmarket?
- `[return_to_previous_topic]`
  - EN: Return to previous topic
  - CZ: Zpět k předchozímu tématu
