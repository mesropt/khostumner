"""Seed data loader for development and testing.

Run with: python -m app.services.seed
Idempotent: checks if data already exists before inserting.
Dev-only: guarded by ENVIRONMENT != "production" check.
"""

import asyncio
import os
import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.elections import Election, ElectionLevel
from app.models.parties import Party
from app.models.politicians import Politician, PoliticianLevel
from app.models.promises import (
    ModerationStatus,
    Promise,
    PromiseElectionLink,
    ResolvedStatus,
)


async def seed(session: AsyncSession) -> None:
    """Insert seed data idempotently. Safe to run on every startup."""

    # Guard: skip in production
    if os.getenv("ENVIRONMENT", "development") == "production":
        print("Seed skipped: production environment")
        return

    # Idempotency: skip if data already present
    result = await session.execute(select(Party).limit(1))
    if result.scalars().first():
        print("Seed data already present — skipping")
        return

    # ------------------------------------------------------------------
    # PARTIES (4)
    # ------------------------------------------------------------------
    civil_contract = Party(
        id=uuid.uuid4(),
        name_hy="Քաղաքացիական պայմանագիր",
        short_name_hy="ՔՊ",
        founded_year=2019,
        notes="[TEST DATA]",
    )
    armenian_revolutionary = Party(
        id=uuid.uuid4(),
        name_hy="Հայ Հեղափոխական Դաշնակցություն",
        short_name_hy="ՀՅԴ",
        founded_year=1890,
        notes="[TEST DATA]",
    )
    prosperous_armenia = Party(
        id=uuid.uuid4(),
        name_hy="Բարգավաճ Հայաստան",
        short_name_hy="ԲՀԿ",
        founded_year=2004,
        notes="[TEST DATA]",
    )
    republican = Party(
        id=uuid.uuid4(),
        name_hy="Հայաստանի Հանրապետական կուսակցություն",
        short_name_hy="ՀՀԿ",
        founded_year=1990,
        notes="[TEST DATA]",
    )
    session.add_all([civil_contract, armenian_revolutionary, prosperous_armenia, republican])
    await session.flush()

    # ------------------------------------------------------------------
    # ELECTIONS (4 — real years per D-18)
    # ------------------------------------------------------------------
    pres_2018 = Election(
        id=uuid.uuid4(),
        name_hy="2018 Նախագահական ընտրություններ",
        slug="presidential-2018",
        election_date=date(2018, 3, 2),
        level=ElectionLevel.national,
    )
    parl_2018 = Election(
        id=uuid.uuid4(),
        name_hy="2018 Ազ.Ժ. ընտրություններ",
        slug="parliamentary-2018",
        election_date=date(2018, 12, 9),
        level=ElectionLevel.national,
    )
    parl_2021 = Election(
        id=uuid.uuid4(),
        name_hy="2021 Ազ.Ժ. ընտրություններ",
        slug="parliamentary-2021",
        election_date=date(2021, 6, 20),
        level=ElectionLevel.national,
    )
    local_2024 = Election(
        id=uuid.uuid4(),
        name_hy="2024 Տեղական ընտրություններ",
        slug="local-2024",
        election_date=date(2024, 9, 17),
        level=ElectionLevel.local,
    )
    session.add_all([pres_2018, parl_2018, parl_2021, local_2024])
    await session.flush()

    # ------------------------------------------------------------------
    # POLITICIANS (10 real names — mixed parties per D-16)
    # ------------------------------------------------------------------
    pashinyan = Politician(
        id=uuid.uuid4(),
        name_hy="Նիկոլ Փաշինյան",
        slug="nikol-pashinyan",
        position="Վարչապետ",
        level=PoliticianLevel.national,
        party_id=civil_contract.id,
        notes="[TEST DATA]",
    )
    armen_sargsyan = Politician(
        id=uuid.uuid4(),
        name_hy="Արմեն Սարգսյան",
        slug="armen-sarkissian",
        position="Նախագահ",
        level=PoliticianLevel.national,
        party_id=None,
        notes="[TEST DATA]",
    )
    serzh_sargsyan = Politician(
        id=uuid.uuid4(),
        name_hy="Սերժ Սարգսյան",
        slug="serzh-sargsyan",
        position="Վարչապետ (նախկին)",
        level=PoliticianLevel.national,
        party_id=republican.id,
        notes="[TEST DATA]",
    )
    tsarukyan = Politician(
        id=uuid.uuid4(),
        name_hy="Գագիկ Ծառուկյան",
        slug="gagik-tsarukyan",
        position="Ազ.Ժ. Պատգամավոր",
        level=PoliticianLevel.national,
        party_id=prosperous_armenia.id,
        notes="[TEST DATA]",
    )
    marukyan = Politician(
        id=uuid.uuid4(),
        name_hy="Եդմոն Մարուկյան",
        slug="edmon-marukyan",
        position="Ազ.Ժ. Պատգամավոր",
        level=PoliticianLevel.national,
        party_id=None,
        notes="[TEST DATA]",
    )
    mirzoyan = Politician(
        id=uuid.uuid4(),
        name_hy="Արարատ Միրզոյան",
        slug="ararat-mirzoyan",
        position="Ազ.Ժ. Նախագահ",
        level=PoliticianLevel.national,
        party_id=civil_contract.id,
        notes="[TEST DATA]",
    )
    grigoryan = Politician(
        id=uuid.uuid4(),
        name_hy="Մհեր Գրիգորյան",
        slug="mher-grigoryan",
        position="Փոխ-Վարչապետ",
        level=PoliticianLevel.national,
        party_id=civil_contract.id,
        notes="[TEST DATA]",
    )
    kerobyan = Politician(
        id=uuid.uuid4(),
        name_hy="Վահան Քերոբյան",
        slug="vahan-kerobyan",
        position="Տնտեսության Նախարար",
        level=PoliticianLevel.national,
        party_id=civil_contract.id,
        notes="[TEST DATA]",
    )
    simonyan = Politician(
        id=uuid.uuid4(),
        name_hy="Ալեն Սիմոնյան",
        slug="alen-simonyan",
        position="Ազ.Ժ. Փոխ-Նախագահ",
        level=PoliticianLevel.national,
        party_id=civil_contract.id,
        notes="[TEST DATA]",
    )
    avinyan = Politician(
        id=uuid.uuid4(),
        name_hy="Տիգրան Ավինյան",
        slug="tigran-avinyan",
        position="Երևանի Քաղաքապետ",
        level=PoliticianLevel.local,
        party_id=civil_contract.id,
        notes="[TEST DATA]",
    )
    session.add_all(
        [
            pashinyan,
            armen_sargsyan,
            serzh_sargsyan,
            tsarukyan,
            marukyan,
            mirzoyan,
            grigoryan,
            kerobyan,
            simonyan,
            avinyan,
        ]
    )
    await session.flush()

    # ------------------------------------------------------------------
    # PROMISES (20 — mixed statuses, all is_seed=True, all moderation_status=approved)
    # Distribution: kept×4, broken×4, in_progress×4, stalled×4, not_rated×4
    # ------------------------------------------------------------------
    promises = [
        # --- KEPT (4) ---
        Promise(
            id=uuid.uuid4(),
            politician_id=pashinyan.id,
            title_hy="Նվազագույն աշխատավարձի բարձրացում",
            quote_hy=(
                "Կբարձրացնեմ նվազագույն աշխատավարձը 150,000 դրամով [TEST DATA]"
            ),
            source_url="https://example.com/p1",
            slug="pashinyan-minimum-wage-2021",
            made_date=date(2021, 5, 1),
            moderation_status=ModerationStatus.approved,
            resolved_status=ResolvedStatus.kept,
            is_seed=True,
        ),
        Promise(
            id=uuid.uuid4(),
            politician_id=pashinyan.id,
            title_hy="Կոռուպցիայի դեմ պայքար",
            quote_hy=(
                "Կտրուկ կկրճատենք կոռուպցիան և կապահովենք թափանցիկ կառավարում [TEST DATA]"
            ),
            source_url="https://example.com/p2",
            slug="pashinyan-anti-corruption-2018",
            made_date=date(2018, 11, 1),
            moderation_status=ModerationStatus.approved,
            resolved_status=ResolvedStatus.kept,
            is_seed=True,
        ),
        Promise(
            id=uuid.uuid4(),
            politician_id=mirzoyan.id,
            title_hy="Ազգային ժողովի բարեփոխումներ",
            quote_hy=(
                "Կիրականացնենք խորհրդարանական կառավարման բարեփոխումներ [TEST DATA]"
            ),
            source_url="https://example.com/p3",
            slug="mirzoyan-parliament-reform-2021",
            made_date=date(2021, 6, 1),
            moderation_status=ModerationStatus.approved,
            resolved_status=ResolvedStatus.kept,
            is_seed=True,
        ),
        Promise(
            id=uuid.uuid4(),
            politician_id=kerobyan.id,
            title_hy="Տնտեսական աճ 7%-ով",
            quote_hy=(
                "Կապահովենք 7 տոկոս տնտեսական աճ մինչև 2023 թ. [TEST DATA]"
            ),
            source_url="https://example.com/p4",
            slug="kerobyan-economic-growth-2021",
            made_date=date(2021, 8, 1),
            moderation_status=ModerationStatus.approved,
            resolved_status=ResolvedStatus.kept,
            is_seed=True,
        ),
        # --- BROKEN (4) ---
        Promise(
            id=uuid.uuid4(),
            politician_id=serzh_sargsyan.id,
            title_hy="Սահմանադրական բարեփոխումներ",
            quote_hy=(
                "Երբ ընդունվի Սահմանադրությունը, Վարչապետ չեմ լինի [TEST DATA]"
            ),
            source_url="https://example.com/p5",
            slug="serzh-constitution-pm-2015",
            made_date=date(2015, 10, 1),
            moderation_status=ModerationStatus.approved,
            resolved_status=ResolvedStatus.broken,
            is_seed=True,
        ),
        Promise(
            id=uuid.uuid4(),
            politician_id=serzh_sargsyan.id,
            title_hy="Ղարաբաղի կարգավիճակ",
            quote_hy=(
                "Ղարաբաղի հարցի լուծման համար կկիրառենք բանակցային ճանապարհ [TEST DATA]"
            ),
            source_url="https://example.com/p6",
            slug="serzh-karabakh-2013",
            made_date=date(2013, 2, 1),
            moderation_status=ModerationStatus.approved,
            resolved_status=ResolvedStatus.broken,
            is_seed=True,
        ),
        Promise(
            id=uuid.uuid4(),
            politician_id=tsarukyan.id,
            title_hy="Բիզնեսի օժանդակություն",
            quote_hy=(
                "Կօժանդակեմ փոքր և միջին բիզնեսի զարգացմանը հատուկ ծրագրերով [TEST DATA]"
            ),
            source_url="https://example.com/p7",
            slug="tsarukyan-sme-support-2017",
            made_date=date(2017, 4, 1),
            moderation_status=ModerationStatus.approved,
            resolved_status=ResolvedStatus.broken,
            is_seed=True,
        ),
        Promise(
            id=uuid.uuid4(),
            politician_id=marukyan.id,
            title_hy="Ընտրական բարեփոխումներ",
            quote_hy=(
                "Կռչնեմ ընտրախախտումների համար արդյունավետ պատժաչափ [TEST DATA]"
            ),
            source_url="https://example.com/p8",
            slug="marukyan-electoral-reform-2017",
            made_date=date(2017, 3, 1),
            moderation_status=ModerationStatus.approved,
            resolved_status=ResolvedStatus.broken,
            is_seed=True,
        ),
        # --- IN PROGRESS (4) ---
        Promise(
            id=uuid.uuid4(),
            politician_id=pashinyan.id,
            title_hy="Դատաիրավական բարեփոխումներ",
            quote_hy=(
                "Կիրականացնենք համապարփակ դատաիրավական բարեփոխումներ [TEST DATA]"
            ),
            source_url="https://example.com/p9",
            slug="pashinyan-judicial-reform-2021",
            made_date=date(2021, 6, 20),
            moderation_status=ModerationStatus.approved,
            resolved_status=ResolvedStatus.in_progress,
            is_seed=True,
        ),
        Promise(
            id=uuid.uuid4(),
            politician_id=grigoryan.id,
            title_hy="Ենթակառուցվածքների զարգացում",
            quote_hy=(
                "Կփոխի ենթակառուցվածքային ծրագրերի ֆինանսավորման մոտեցումը [TEST DATA]"
            ),
            source_url="https://example.com/p10",
            slug="grigoryan-infrastructure-2021",
            made_date=date(2021, 8, 15),
            moderation_status=ModerationStatus.approved,
            resolved_status=ResolvedStatus.in_progress,
            is_seed=True,
        ),
        Promise(
            id=uuid.uuid4(),
            politician_id=avinyan.id,
            title_hy="Երևանի փոխադրամիջոցների բարեփոխում",
            quote_hy=(
                "Կիրականացնեմ Երևանի հասարակական տրանսպորտի արդիականացում [TEST DATA]"
            ),
            source_url="https://example.com/p11",
            slug="avinyan-yerevan-transport-2024",
            made_date=date(2024, 10, 1),
            moderation_status=ModerationStatus.approved,
            resolved_status=ResolvedStatus.in_progress,
            is_seed=True,
        ),
        Promise(
            id=uuid.uuid4(),
            politician_id=simonyan.id,
            title_hy="Խորհրդարանական հանձնաժողովների թափանցիկություն",
            quote_hy=(
                "Կապահովեմ խորհրդարանական հանձնաժողովների աշխատանքի հրապարակայնություն [TEST DATA]"
            ),
            source_url="https://example.com/p12",
            slug="simonyan-committee-transparency-2021",
            made_date=date(2021, 7, 1),
            moderation_status=ModerationStatus.approved,
            resolved_status=ResolvedStatus.in_progress,
            is_seed=True,
        ),
        # --- STALLED (4) ---
        Promise(
            id=uuid.uuid4(),
            politician_id=pashinyan.id,
            title_hy="Կրթական բարեփոխումներ",
            quote_hy=(
                "Կկատարեմ կրթական համակարգի հիմնական փոփոխություններ 2020-ի ընթացքում [TEST DATA]"
            ),
            source_url="https://example.com/p13",
            slug="pashinyan-education-reform-2018",
            made_date=date(2018, 11, 15),
            moderation_status=ModerationStatus.approved,
            resolved_status=ResolvedStatus.stalled,
            is_seed=True,
        ),
        Promise(
            id=uuid.uuid4(),
            politician_id=tsarukyan.id,
            title_hy="Գյուղատնտեսության աջակցություն",
            quote_hy=(
                "Կազդարարեմ ֆերմերների համար 20 մլրդ դրամ դրամաշնորհ [TEST DATA]"
            ),
            source_url="https://example.com/p14",
            slug="tsarukyan-agriculture-grant-2021",
            made_date=date(2021, 5, 20),
            moderation_status=ModerationStatus.approved,
            resolved_status=ResolvedStatus.stalled,
            is_seed=True,
        ),
        Promise(
            id=uuid.uuid4(),
            politician_id=marukyan.id,
            title_hy="Հակամենաշնորհային կարգավորում",
            quote_hy=(
                "Կներկայացնեմ հակամենաշնորհային օրենսդրության բարեփոխման փաթեթ [TEST DATA]"
            ),
            source_url="https://example.com/p15",
            slug="marukyan-antitrust-2021",
            made_date=date(2021, 6, 1),
            moderation_status=ModerationStatus.approved,
            resolved_status=ResolvedStatus.stalled,
            is_seed=True,
        ),
        Promise(
            id=uuid.uuid4(),
            politician_id=armen_sargsyan.id,
            title_hy="Ռազմավարական ներդրումների ապահովում",
            quote_hy=(
                "Կկյուղաղ կշուռ տայ արտաքին ռազմավարական ներդրումների ապահովմանը [TEST DATA]"
            ),
            source_url="https://example.com/p16",
            slug="armen-sargsyan-investments-2018",
            made_date=date(2018, 4, 9),
            moderation_status=ModerationStatus.approved,
            resolved_status=ResolvedStatus.stalled,
            is_seed=True,
        ),
        # --- NOT RATED (4) ---
        Promise(
            id=uuid.uuid4(),
            politician_id=pashinyan.id,
            title_hy="Թվային կառավարության ծառայություններ",
            quote_hy=(
                "Կտեղափոխեմ պետական ծառայությունների 80%-ը թվային ձևաչափի [TEST DATA]"
            ),
            source_url="https://example.com/p17",
            slug="pashinyan-digital-gov-2024",
            made_date=date(2024, 9, 1),
            moderation_status=ModerationStatus.approved,
            resolved_status=ResolvedStatus.not_rated,
            is_seed=True,
        ),
        Promise(
            id=uuid.uuid4(),
            politician_id=avinyan.id,
            title_hy="Երևան — կանաչ քաղաք",
            quote_hy=(
                "Կավելացնեմ Երևանի կանաչ տարածքները 30%-ով 2026-ի ընթացքում [TEST DATA]"
            ),
            source_url="https://example.com/p18",
            slug="avinyan-green-yerevan-2024",
            made_date=date(2024, 10, 15),
            moderation_status=ModerationStatus.approved,
            resolved_status=ResolvedStatus.not_rated,
            is_seed=True,
        ),
        Promise(
            id=uuid.uuid4(),
            politician_id=simonyan.id,
            title_hy="Պատգամավորների հայտարարագրերի ստուգում",
            quote_hy=(
                "Կկազմակերպեմ պատգամավորների ունեցվածքի հայտարարագրերի արտաքին աուդիտ [TEST DATA]"
            ),
            source_url="https://example.com/p19",
            slug="simonyan-mp-declarations-2024",
            made_date=date(2024, 8, 1),
            moderation_status=ModerationStatus.approved,
            resolved_status=ResolvedStatus.not_rated,
            is_seed=True,
        ),
        Promise(
            id=uuid.uuid4(),
            politician_id=grigoryan.id,
            title_hy="Հյուսիս-հարավ ավտոմայրուղի",
            quote_hy=(
                "Կկomplete Հյուսիս-հարավ ավտոմայրուղու կառուցումն ըստ ժամանակացույցի [TEST DATA]"
            ),
            source_url="https://example.com/p20",
            slug="grigoryan-north-south-highway-2024",
            made_date=date(2024, 7, 1),
            moderation_status=ModerationStatus.approved,
            resolved_status=ResolvedStatus.not_rated,
            is_seed=True,
        ),
    ]
    session.add_all(promises)
    await session.flush()

    # ------------------------------------------------------------------
    # PROMISE-ELECTION LINKS (link select promises to elections)
    # ------------------------------------------------------------------
    links = [
        PromiseElectionLink(
            id=uuid.uuid4(),
            promise_id=promises[0].id,   # pashinyan min wage -> parl_2021
            election_id=parl_2021.id,
        ),
        PromiseElectionLink(
            id=uuid.uuid4(),
            promise_id=promises[1].id,   # pashinyan anti-corruption -> parl_2018
            election_id=parl_2018.id,
        ),
        PromiseElectionLink(
            id=uuid.uuid4(),
            promise_id=promises[4].id,   # serzh constitution -> pres_2018
            election_id=pres_2018.id,
        ),
        PromiseElectionLink(
            id=uuid.uuid4(),
            promise_id=promises[8].id,   # pashinyan judicial reform -> parl_2021
            election_id=parl_2021.id,
        ),
        PromiseElectionLink(
            id=uuid.uuid4(),
            promise_id=promises[16].id,  # pashinyan digital gov -> local_2024
            election_id=local_2024.id,
        ),
    ]
    session.add_all(links)

    await session.commit()
    print("Seed data inserted successfully")


async def _run_seed() -> None:
    async with AsyncSessionLocal() as session:
        await seed(session)


if __name__ == "__main__":
    asyncio.run(_run_seed())
