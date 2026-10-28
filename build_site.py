#!/usr/bin/env python3
"""Generate the static Runnymede Parking Review pages from the proposal data."""

from html import escape
from pathlib import Path
import json
import re


ROOT = Path(__file__).resolve().parent
FORM_URL = "https://runnymedeparkingreview2026.commonplace.is/"
STATEMENT_URL = (
    "https://www.surreycc.gov.uk/__data/assets/pdf_file/0004/539329/"
    "Runnymede-parking-review-2026.-Statement-of-Reasons.pdf"
)

# Each map tuple is (local PDF filename, page number, drawing reference).
PROPOSALS = [
    {
        "id": "corrie-bois-hall",
        "area": "addlestone",
        "title": "Corrie Road and Bois Hall Road",
        "division": "Addlestone",
        "drawings": ["AD12"],
        "maps": [("addlestone-part-1.pdf", 1, "AD12")],
        "details": [
            "Introduce double yellow lines on both sides of Corrie Road where it becomes Bois Hall Road over The Bourne stream to prevent parking, improve sightlines and maintain access at all times.",
            "On the east side, the lines extend from the southern side of Pitson Close along Corrie Road, over the bridge and into the northern side of Bourneside Road. On the west side, they extend from the southern boundary of No. 24 Corrie Road over the bridge and round to the entrance of Waters Edge. A further length runs around the grassed build-out on the west side of Bois Hall Road, south of the Waters Edge junction.",
        ],
    },
    {
        "id": "chapel-park-chapel-grove",
        "area": "addlestone",
        "title": "Chapel Park Road junction with Chapel Grove",
        "division": "Addlestone",
        "drawings": ["AD13"],
        "maps": [("addlestone-part-1.pdf", 2, "AD13")],
        "details": [
            "Install a length of double yellow line on the inside of the junction between Chapel Grove and Chapel Park Road, on the corner outside No. 56, to improve sightlines and maintain access at all times.",
        ],
    },
    {
        "id": "green-lane-rickman-crescent",
        "area": "addlestone",
        "title": "Green Lane junctions with Rickman Crescent",
        "division": "Addlestone",
        "drawings": ["AD14"],
        "maps": [("addlestone-part-1.pdf", 3, "AD14")],
        "details": [
            "Install 18 metres of double yellow lines at both junctions of Rickman Crescent with Green Lane to improve sightlines and maintain access at all times.",
        ],
    },
    {
        "id": "hamm-moor-lane",
        "area": "addlestone",
        "title": "Hamm Moor Lane",
        "division": "Addlestone",
        "drawings": ["AD15"],
        "maps": [("addlestone-part-1.pdf", 4, "AD15")],
        "details": [
            "On the east side of Hamm Moor Lane, introduce a 30-metre Monday to Saturday, 8am to 6pm, 2 hours, no return within 2 hours parking bay. It will begin south of the existing double yellow lines and extend southwards.",
            "This is currently an unrestricted space occupied by long-term parking. A time-limited bay would give customers of local businesses a place to stop, improving compliance and safety. Customers currently park dangerously on double yellow lines because there are few short-term spaces.",
        ],
    },
    {
        "id": "ledger-drive-rudge-rise",
        "area": "addlestone",
        "title": "Ledger Drive junction with Rudge Rise",
        "division": "Addlestone",
        "drawings": ["AD16"],
        "maps": [("addlestone-part-2.pdf", 1, "AD16")],
        "details": [
            "Install double yellow lines at the junction of Ledger Drive and Rudge Rise to improve sightlines and maintain access at all times.",
        ],
    },
    {
        "id": "lime-grove-sumner-place",
        "area": "addlestone",
        "title": "Lime Grove junction with Sumner Place",
        "division": "Addlestone",
        "drawings": ["AD17"],
        "maps": [("addlestone-part-2.pdf", 2, "AD17")],
        "details": [
            "Runnymede Borough Council's waste collection team has requested double yellow lines because its dustcart cannot always access Sumner Place due to parked vehicles. The proposal is to install double yellow lines at this junction and opposite Sumner Place on Lime Grove to improve sightlines and maintain access at all times.",
        ],
    },
    {
        "id": "sayes-court-farm-drive",
        "area": "addlestone",
        "title": "Sayes Court Farm Drive",
        "division": "Addlestone",
        "drawings": ["AD18"],
        "maps": [("addlestone-part-2.pdf", 3, "AD18")],
        "details": [
            "As recommended in the Road Safety Outside Schools report for Sayes Court Primary School, introduce a new 25.56-metre School Keep Clear sign and road marking south of the existing one. It would operate Monday to Friday, 8.15am to 9.15am and 2.30pm to 4pm.",
            "The restriction would protect the vehicle exit, pedestrian access and sightlines from these school access points.",
        ],
    },
    {
        "id": "essex-close",
        "area": "addlestone",
        "title": "Essex Close",
        "division": "Addlestone",
        "drawings": ["AD19"],
        "maps": [("addlestone-part-2.pdf", 4, "AD19")],
        "details": [
            "Install a single yellow line around the perimeter of Essex Close, operating Monday to Friday between 10am and noon. The lines are intended to deter non-residents from parking all day while they work in town, giving Essex Close residents a greater opportunity to park closer to their homes.",
        ],
    },
    {
        "id": "school-lane",
        "area": "addlestone",
        "title": "School Lane",
        "division": "Addlestone",
        "drawings": ["AD20"],
        "maps": [("addlestone-part-2.pdf", 5, "AD20")],
        "details": [
            "On behalf of the Road Safety and School Active Travel Team, introduce three separate School Keep Clear markings at the southern end of School Lane, either side of and between the entrance and exit roads to Jubilee High School and St Paul's C of E Primary School. They would operate Monday to Friday, 8.15am to 9.15am and 2.30pm to 4pm.",
            "The markings would create a no-stopping zone on the west side of School Lane, improving sightlines and visibility for pupils and staff crossing the road at the beginning and end of the school day.",
        ],
    },
    {
        "id": "bridge-road",
        "area": "chertsey",
        "title": "Bridge Road",
        "division": "Chertsey",
        "drawings": ["CH19"],
        "maps": [("chertsey-part-1.pdf", 1, "CH19")],
        "details": [
            "On the north side of Bridge Road, install double yellow lines to fill the unrestricted gap between Abbey Meadows and the existing double yellow lines at the junction to the camping grounds entrance. On the south side, extend double yellow lines westwards from where the existing restrictions end by The Planes to join the existing lines outside No. 46.",
            "Bridge Road (B375) is a major arterial route with high traffic volumes. Vehicles parked partly on the footway and partly on the carriageway in unrestricted sections inhibit traffic flow and cause local congestion. They also block the footway, particularly on the narrow north side. The lines would maintain traffic flow and keep footways clear for pedestrians.",
        ],
    },
    {
        "id": "fordwater-road",
        "area": "chertsey",
        "title": "Fordwater Road",
        "division": "Chertsey",
        "drawings": ["CH20"],
        "maps": [("chertsey-part-1.pdf", 2, "CH20")],
        "details": [
            "Introduce double yellow lines on the west side of Fordwater Road in front of and either side of the entrance to No. 62a, LB Demolition and Haulage Ltd. The lines would incorporate the existing white hatching, which is regularly ignored, causing blocked sightlines and access problems.",
        ],
    },
    {
        "id": "paddocks-way",
        "area": "chertsey",
        "title": "Paddocks Way",
        "division": "Chertsey",
        "drawings": ["CH21"],
        "maps": [("chertsey-part-1.pdf", 3, "CH21")],
        "details": [
            "Extend the double yellow lines on the south side of Paddocks Way 9 metres westwards from the junction with Fordwater Road to improve access into Paddocks Way.",
            "Introduce double yellow lines around the inside of the bend, from alongside the garage at the rear of No. 40 Fordwater Road to the dropped kerb at No. 1 Paddocks Way. These lines would improve sightlines and maintain access at all times.",
        ],
    },
    {
        "id": "station-road",
        "area": "chertsey",
        "title": "Station Road",
        "division": "Chertsey",
        "drawings": ["CH22"],
        "maps": [("chertsey-part-2.pdf", 1, "CH22")],
        "details": [
            "Revoke 20 metres of the existing Monday to Saturday, 8am to 6pm single yellow line on the north side of Station Road, west of the junction with Charles Street, beginning where the double yellow lines end. This would create an unrestricted space that can be used for parking.",
        ],
    },
    {
        "id": "windsor-street",
        "area": "chertsey",
        "title": "Windsor Street",
        "division": "Chertsey",
        "drawings": ["CH23"],
        "maps": [("chertsey-part-2.pdf", 2, "CH23")],
        "details": [
            "On the west side of Windsor Street, introduce Monday to Saturday, 8am to 6pm, 30 minutes, no return within 30 minutes time-limited parking bays. The bays would run outside No. 3 (Simpsons Chicken) to No. 15 (Hodders), and from No. 17 to No. 23 (Windsor Wine and Dine).",
            "The restriction is intended to provide a regular turnover of vehicles, making spaces more available to passing motorists and allowing more customers to visit local shops and amenities.",
        ],
    },
    {
        "id": "little-green-lane",
        "area": "chertsey",
        "title": "Little Green Lane (Meadowcroft School)",
        "division": "Chertsey",
        "drawings": ["CH24"],
        "maps": [("chertsey-part-2.pdf", 3, "CH24")],
        "details": [
            "On behalf of the Road Safety and School Active Travel Team, extend the existing double yellow lines on the north side of Little Green Lane from the Inglewood junction by 18 metres. Add double yellow lines on both corners of the Merrylands junction, extending 10 metres.",
            "Add 37.2 metres of School Keep Clear markings, located 45 metres east of the centre line of Inglewood and 45 metres west of the centre line of Jersey Close. On the south side, add double yellow lines on the westernmost table from 30 metres from the dropped kerb at No. 104 to the edge of the table, and on the easternmost table from the dropped kerb at No. 120 for 13 metres to the edge of the table.",
            "The measures respond to Meadowcroft School's expansion and are intended to encourage walking to school and create a safer environment for pedestrians, particularly children. Speed tables will slow traffic and enable easier crossing. Double yellow lines will protect crossing-point sightlines and prevent inconsiderate parking at road narrowings and give-way lines.",
        ],
    },
    {
        "id": "boscombe-close",
        "area": "egham",
        "title": "Boscombe Close",
        "division": "Egham",
        "drawings": ["EG17"],
        "maps": [("egham.pdf", 1, "EG17")],
        "details": [
            "Install double yellow lines at the junction of Boscombe Close and the B388 Thorpe Lea Road. The restrictions would mainly extend eastwards on both sides of Boscombe Close to prevent parking too close to the junction, improve sightlines and maintain access at all times.",
        ],
    },
    {
        "id": "claremont-road",
        "area": "egham",
        "title": "Claremont Road",
        "division": "Egham",
        "drawings": ["EG18"],
        "maps": [("egham.pdf", 2, "EG18")],
        "details": [
            "Extend double yellow lines southwards on both sides of Claremont Road, south of the junction with the A308 The Causeway, to maintain access at all times. Vehicles currently park beyond the ends of the restrictions and overlap dropped kerbs, restricting access to Nos. 59 to 72 Claremont Road and the two-storey office block opposite.",
        ],
    },
    {
        "id": "roundway",
        "area": "egham",
        "title": "Roundway",
        "division": "Egham",
        "drawings": ["EG19"],
        "maps": [("egham.pdf", 3, "EG19")],
        "details": [
            "Introduce double yellow lines on both sides of the south-western bend. On the inside of the bend, the lines would run from the start of the dropped kerb at No. 27, next to the disabled parking bay, round to the end of the grass verge outside No. 31. This would stop parking on the verge and maintain access at all times.",
            "On the outside of the bend, the lines would run from outside No. 50 to No. 68 to protect residential accesses, maintain access and stop obstructive pavement parking.",
        ],
    },
    {
        "id": "vicarage-road-vicarage-avenue",
        "area": "egham",
        "title": "Vicarage Road junction with Vicarage Avenue",
        "division": "Egham",
        "drawings": ["EG20"],
        "maps": [("egham.pdf", 4, "EG20")],
        "details": [
            "Install double yellow lines at the junction of Vicarage Road and Vicarage Avenue to improve sightlines and maintain access at all times.",
        ],
    },
    {
        "id": "central-englefield-green-permit-scheme",
        "area": "englefield-green",
        "title": "Central Englefield Green permit scheme",
        "division": "Englefield Green",
        "drawings": ["ENG19", "ENG20", "ENG21", "ENG22"],
        "maps": [
            ("englefield-green-permit-area.pdf", 1, "ENG19"),
            ("englefield-green-permit-area.pdf", 2, "ENG20"),
            ("englefield-green-permit-area.pdf", 3, "ENG21"),
            ("englefield-green-permit-area.pdf", 4, "ENG22"),
            ("englefield-green-permit-detailed.pdf", 1, "ENG20 (detailed)"),
            ("englefield-green-permit-detailed.pdf", 2, "ENG21 (detailed)"),
            ("englefield-green-permit-detailed.pdf", 3, "ENG22 (detailed)"),
        ],
        "details": [
            "Introduce a permit parking area identified as Zone G, operating Monday to Saturday, 7am to 8pm. A maximum of two residents' permits may be issued to each eligible household.",
            "Royal Holloway's accommodation policy excludes students living in halls from applying for on-street permits. The following halls are excluded: all apartments in Parfitt, Preedy, Townsend, Beddoe and McDonald Buildings at The Garage, 98 Harvest Road, TW20 0QR; and all apartments in Blocks A1, A2, B1, B2, B3, C1 and C2 of George Eliot Hall, Harvest Road, TW20 0BN.",
            "A 12-metre Loading Only bay is proposed outside The Happy Man pub, Harvest Road, TW20 0QS.",
            "Eligible resident permit properties are:",
            "- Parsonage Road (full length): Nos. 1, 6, 8 and 10.",
            "- Harvest Road (Barnway to South Road): Nos. 2, 4, 8, 9, 10, 11, The Happy Man pub and its flat, 12A, 14 to 30, flats 1 to 5 at No. 33, Nos. 41 to 48, flats 1 to 4 at No. 49, Nos. 52 to 59, 78 to 83, 86, 89 and 90.",
            "- Albert Road (full length): Nos. 1 to 10, 13, 15 to 29 and 47.",
            "- Armstrong Road (full length): Nos. 1 to 18, 24 to 31, 31a, 34 and 39.",
            "- Alexandra Road (east of Englefield Close to South Road): Nos. 1 to 9, 11, 12, 14 to 16, 19 to 26, 28 to 30, 35, 36, 38 to 43, 49 to 52, 57 to 64, 64a and 64b.",
            "- South Road (full length): Nos. 2a to 2d, 3a, 4a, 9 to 26.",
            "Visitor permits are also available to additional properties: Parsonage Road Nos. 3, 5, 7, 9, 11, 13, 15, 17, 19, 2, the Annex at 2, and 4, 18, 20, 22, 24, 26 and 28; Harvest Road Nos. 3, 4A, 5, 6, 7, 40, 74 to 77, 84, 90a, 95, 96 and 96a; Albert Road Nos. 11, 12, 14, 45 and 46, and Nos. 1 to 6 Mary Drew Almshouses; Armstrong Road Nos. 31, 31b to 31e, 32, 32a, 33, 34a, 34b, 35, 36, 37, 37a, 37b, 38, 40, 42 to 45, and Nos. 1 to 11 Armstrong Mews; Alexandra Road Nos. 10, 13, 17, 18, 27, 27a, 37 and 44 to 48; South Road Nos. 1a, 5a (Chapel End), 1, 2, 7 and 11.",
            "Residents' permits are valid for one year and cost £88 for the first permit and £108 for the second. Households with off-street parking for two or more vehicles are not eligible for residents' permits; households with one off-street space and multiple cars may have one permit; households with no off-street parking may have up to two.",
            "Each household may buy up to 150 all-day visitor permits per year at £2 each, and up to 250 two-hour visitor permits per year at £1 each. Each visitor permit is valid for one day, and visitor vehicles must display a permit during scheme hours. Child-care permits cost £108 per year. Replacing a lost permit or updating vehicle details costs £15.",
            "Blue Badge holders may park in the permit area for as long as needed when displaying their badge. Housebound residents who need regular care visits can apply for a free annual carers' permit. Deliveries and loading or unloading are allowed for as long as necessary, up to 20 minutes.",
        ],
    },
    {
        "id": "armstrong-road",
        "area": "englefield-green",
        "title": "Armstrong Road",
        "division": "Englefield Green",
        "drawings": ["ENG23", "ENG24"],
        "maps": [
            ("englefield-green-part-1.pdf", 1, "ENG23"),
            ("englefield-green-part-1.pdf", 2, "ENG24"),
        ],
        "details": [
            "Introduce a no-waiting-at-any-time restriction (double yellow lines) along the full length of the west side of Armstrong Road, including the existing single yellow line between the boundary of The Garage and No. 39 southwards and No. 36.",
            "Armstrong Road is narrow and vehicles park in a line on the east side. Vehicles parked on the west side at any time obstruct the road.",
        ],
    },
    {
        "id": "middle-hill-permit-bays",
        "area": "englefield-green",
        "title": "Middle Hill permit bays",
        "division": "Englefield Green",
        "drawings": ["ENG25"],
        "maps": [("englefield-green-part-1.pdf", 3, "ENG25")],
        "details": [
            "Introduce four residents' permit-holder-only parking bays on Middle Hill, identified as Zone H and operating Monday to Saturday, 7am to 8pm. The first bay would be outside No. 25, in the gap between the two lengths of existing double yellow lines. The second would extend from the east boundary of No. 27 westwards up Middle Hill to the double yellow lines outside The Beehive pub. The third would be 10 metres long outside Nos. 46 and 47. The fourth would extend from the east building line of No. 49 westwards to the west building line of No. 56.",
            "Residents' permits are valid for one year and cost £88 for the first, £108 for the second and £138 for the third and subsequent permits. The maximum number of permits per household is the number of registered household vehicles minus the property's off-street parking spaces. Residents with adequate off-street parking are not eligible for residents' permits but may buy visitor permits.",
            "Each household may buy up to 150 all-day visitor permits per year at £2 each, and up to 250 two-hour visitor permits per year at £1 each. Each visitor permit is valid for one day; visitor vehicles must display a permit during scheme hours. Child-care permits cost £108 per year. Replacing a lost permit or updating vehicle details costs £15.",
            "Blue Badge holders may park in the permit area for as long as needed when displaying their badge. Housebound residents who need regular care visits can apply for a free annual carers' permit. Deliveries and loading or unloading are allowed for as long as necessary, up to 20 minutes.",
            "Eligible for residents' permits: Nos. 10 to 13, 27 to 32, 46, 47 (Blacklock House), and 49 to 55 Middle Hill. Eligible for visitor permits only: Nos. 9, 26 and 56 (Hillside Cottage).",
        ],
    },
    {
        "id": "middle-hill-spencer-gardens",
        "area": "englefield-green",
        "title": "Middle Hill junction with Spencer Gardens",
        "division": "Englefield Green",
        "drawings": ["ENG30"],
        "maps": [("englefield-green-part-3.pdf", 2, "ENG30")],
        "details": [
            "Install double yellow lines at the junction of Middle Hill and Spencer Gardens to improve sightlines and maintain access at all times.",
        ],
    },
    {
        "id": "middle-hill-lodge-close",
        "area": "englefield-green",
        "title": "Middle Hill junction with Lodge Close",
        "division": "Englefield Green",
        "drawings": ["ENG25"],
        "maps": [("englefield-green-part-1.pdf", 3, "ENG25")],
        "details": [
            "Install double yellow lines on Middle Hill, starting east of the third parking bay outside No. 46, extending eastwards across the frontage of Fagins Cottage and Olivers Cottage, and round onto the west side of Lodge Close up to a point in line with the existing restrictions on the opposite side. This would prevent parking on the junction and maintain sightlines and access at all times.",
        ],
    },
    {
        "id": "the-retreat",
        "area": "englefield-green",
        "title": "The Retreat",
        "division": "Englefield Green",
        "drawings": ["ENG25"],
        "maps": [("englefield-green-part-1.pdf", 3, "ENG25")],
        "details": [
            "Install double yellow lines on the west/north side of The Retreat. The restriction would extend from where it currently ends outside No. 13, south and westwards to a point in line with the building line of No. 12, to prevent double parking, improve sightlines and maintain access at all times.",
        ],
    },
    {
        "id": "st-judes-road-west-tro-amendment",
        "area": "englefield-green",
        "title": "St Judes Road (west side) — Traffic Regulation Order amendment",
        "division": "Englefield Green",
        "drawings": ["ENG26"],
        "maps": [("englefield-green-part-2.pdf", 1, "ENG26")],
        "details": [
            "Remove from the Traffic Regulation Order the no-loading-at-any-time restriction on the west side of St Judes Road, from outside No. 73 north to No. 78. The restriction is not signed or marked on the kerbs and is not required on the street.",
        ],
    },
    {
        "id": "st-judes-road-east-tro-amendment",
        "area": "englefield-green",
        "title": "St Judes Road (east side) — Traffic Regulation Order amendment",
        "division": "Englefield Green",
        "drawings": ["ENG26"],
        "maps": [("englefield-green-part-2.pdf", 1, "ENG26")],
        "details": [
            "Remove from the Traffic Regulation Order the no-loading-at-any-time restriction on the east side of St Judes Road, from the limited waiting bay on the south side of Victoria Street southwards to the junction with Alexandra Road. The restriction contradicts the bus stop, is not signed or marked on the kerbs and is not required on the street.",
        ],
    },
    {
        "id": "victoria-street-tro-amendment",
        "area": "englefield-green",
        "title": "Victoria Street — Traffic Regulation Order amendment",
        "division": "Englefield Green",
        "drawings": ["ENG23", "ENG26"],
        "maps": [
            ("englefield-green-part-1.pdf", 1, "ENG23"),
            ("englefield-green-part-2.pdf", 1, "ENG26"),
        ],
        "details": [
            "Remove from the Traffic Regulation Order the no-loading-at-any-time restriction on the north side of Victoria Street, from outside No. 33b eastwards to No. 41. The restriction is not signed or marked on the kerbs and is not required on the street.",
        ],
    },
    {
        "id": "wick-road",
        "area": "englefield-green",
        "title": "Wick Road",
        "division": "Englefield Green",
        "drawings": ["ENG28"],
        "maps": [("englefield-green-part-2.pdf", 3, "ENG28")],
        "details": [
            "Extend the double yellow lines on the south side of the street 5 metres westwards up to the Permit Holders Only entry sign. This would prevent nuisance parking in the gap between the end of the existing double yellow line and the sign.",
        ],
    },
    {
        "id": "barnway",
        "area": "englefield-green",
        "title": "Barnway",
        "division": "Englefield Green",
        "drawings": ["ENG31"],
        "maps": [("englefield-green-part-3.pdf", 3, "ENG31")],
        "details": [
            "Install a single yellow line around the perimeter of Barnway, enforceable Monday to Friday, 10am to noon. This is intended to prevent all-day, long-term parking by non-residents that interferes with residents' parking needs.",
        ],
    },
    {
        "id": "spring-rise",
        "area": "egham",
        "title": "Spring Rise",
        "division": "Englefield Green division — Egham area",
        "drawings": ["ENG27"],
        "maps": [("englefield-green-part-2.pdf", 2, "ENG27")],
        "details": [
            "Install double yellow lines on the east side of Spring Rise to maintain access at all times. The current unrestricted gap between No. 117 and Egham United Services Club would be filled, limiting parking to one side of Spring Rise.",
            "When events are held at the club, vehicles park on both sides of Spring Rise, blocking the road and making it difficult for through traffic to pass.",
        ],
    },
    {
        "id": "denham-road-tro-amendment",
        "area": "egham",
        "title": "Denham Road — Traffic Regulation Order amendment",
        "division": "Englefield Green division — Egham area",
        "drawings": ["ENG29"],
        "maps": [("englefield-green-part-3.pdf", 1, "ENG29")],
        "details": [
            "Amend the Traffic Regulation Order to match the restrictions on the east side of Denham Road opposite Nos. 11 to 17. The Monday to Saturday, 8am to 6pm, 30 minutes, no return within 30 minutes parking bay extends southwards to a point opposite the boundary of Nos. 16 and 17, 4.5 metres further than shown in the order.",
            "South of the bay, at the courtyard entrance, the on-street restriction is no waiting at any time (double yellow lines), not the Monday to Saturday, 8am to 6pm restriction currently stated in the order.",
        ],
    },
    {
        "id": "bousley-rise",
        "area": "ottershaw",
        "title": "Bousley Rise",
        "division": "Foxhills, Thorpe and Virginia Water",
        "drawings": ["FTV12"],
        "maps": [("foxhills-thorpe-virginia-water.pdf", 1, "FTV12")],
        "details": [
            "As recommended in the Road Safety Outside Schools report for Ottershaw Christ Church Church of England Infant and Junior Schools, replace and extend the existing H-bar access protection marking across the frontage of a doctor's surgery with double yellow lines.",
            "The lines would keep the access clear and provide a larger passing place within the line of parked vehicles. There is currently congestion because there is insufficient space for two vehicles to pass parked cars, leading some motorists to pull onto the footway in conflict with pedestrians.",
        ],
    },
    {
        "id": "brox-road",
        "area": "ottershaw",
        "title": "Brox Road",
        "division": "Foxhills, Thorpe and Virginia Water",
        "drawings": ["FTV13"],
        "maps": [("foxhills-thorpe-virginia-water.pdf", 2, "FTV13")],
        "details": [
            "Following a road safety audit for the new housing development, introduce double yellow lines on and around the Duffins Orchard, Hawthorn Road and Brox Lane junctions with Brox Road. The restrictions would maintain sightlines on the side roads and allow traffic to flow along Brox Road.",
        ],
    },
    {
        "id": "crabtree-road",
        "area": "thorpe",
        "title": "Crabtree Road",
        "division": "Foxhills, Thorpe and Virginia Water",
        "drawings": ["FTV14"],
        "maps": [("foxhills-thorpe-virginia-water.pdf", 3, "FTV14")],
        "details": [
            "Introduce double yellow lines on Crabtree Road opposite the junction with Eversley Way. Royal Mail staff park in available spaces during the day, and vans are regularly parked on the grass opposite the junction, preventing coaches from entering or leaving a depot in Eversley Way.",
            "The restriction would create a passing place on Crabtree Road, prevent parking opposite the junction, improve sightlines and maintain access at all times.",
        ],
    },
    {
        "id": "stroude-road-luddington-avenue",
        "area": "virginia-water",
        "title": "Stroude Road junction with Luddington Avenue",
        "division": "Foxhills, Thorpe and Virginia Water",
        "drawings": ["FTV15"],
        "maps": [("foxhills-thorpe-virginia-water.pdf", 4, "FTV15")],
        "details": [
            "Install double yellow lines at the junction of Stroude Road and Luddington Avenue to improve sightlines and maintain access at all times.",
        ],
    },
    {
        "id": "woodham-lane-new-haw",
        "area": "new-haw",
        "title": "Woodham Lane (New Haw)",
        "division": "Woodham and New Haw",
        "drawings": ["WNH17", "WNH18"],
        "maps": [
            ("woodham-new-haw.pdf", 1, "WNH17"),
            ("woodham-new-haw.pdf", 2, "WNH18"),
        ],
        "details": [
            "Introduce a no-waiting-at-any-time restriction (double yellow lines) on the east side of Woodham Lane. The restriction would extend from where the existing yellow lines end opposite No. 6, near the mini-roundabout by New Haw Lock, southwards to the southern building line of No. 4 Common Lane.",
            "The B385 is a busy route used by buses and heavy goods vehicles. Vehicles parked partly on the footway inhibit pedestrians, can cause congestion at peak times and block sightlines for vehicles exiting properties from Lock House to No. 13 Woodham Lane.",
        ],
    },
    {
        "id": "woodham-lane-hawthorn-way",
        "area": "new-haw",
        "title": "Woodham Lane junction with Hawthorn Way",
        "division": "Woodham and New Haw",
        "drawings": ["WNH19"],
        "maps": [("woodham-new-haw.pdf", 3, "WNH19")],
        "details": [
            "At Runnymede Borough Council's request, install double yellow lines at the junction of Woodham Lane and Hawthorn Way to improve access for dustcarts and other large vehicles at all times.",
        ],
    },
    {
        "id": "woodham-lane-mayfield-avenue",
        "area": "new-haw",
        "title": "Woodham Lane junction with Mayfield Avenue",
        "division": "Woodham and New Haw",
        "drawings": ["WNH20"],
        "maps": [("woodham-new-haw.pdf", 4, "WNH20")],
        "details": [
            "Extend the double yellow lines on the south side of Mayfield Avenue 13 metres westwards to bring the restriction in line with the existing double yellow lines on the north side. This would move parked vehicles further from the junction with Woodham Lane, creating additional space for turning and queuing vehicles and improving road safety.",
        ],
    },
    {
        "id": "woodham-lane-woodham",
        "area": "woodham",
        "title": "Woodham Lane (Woodham)",
        "division": "Woodham and New Haw",
        "drawings": ["WNH21", "WNH22"],
        "maps": [
            ("woodham-new-haw.pdf", 5, "WNH21"),
            ("woodham-new-haw.pdf", 6, "WNH22"),
        ],
        "details": [
            "In response to several requests, introduce double yellow lines on the north side of Woodham Lane from the roundabout at the junction with The Broadway westwards to No. 334, mirroring the restriction on the south side. This would prevent vehicles displaced from the south side relocating to the north and obstructing through traffic.",
        ],
    },
]

AREAS = [
    ("addlestone", "Addlestone", "Addlestone division"),
    ("chertsey", "Chertsey", "Chertsey division"),
    ("egham", "Egham", "Egham and Englefield Green division proposals"),
    ("englefield-green", "Englefield Green", "Englefield Green division"),
    ("ottershaw", "Ottershaw", "Foxhills, Thorpe and Virginia Water division"),
    ("thorpe", "Thorpe", "Foxhills, Thorpe and Virginia Water division"),
    ("virginia-water", "Virginia Water", "Foxhills, Thorpe and Virginia Water division"),
    ("new-haw", "New Haw", "Woodham and New Haw division"),
    ("woodham", "Woodham", "Woodham and New Haw division"),
]

FEEDBACK_TEXT = [
    "There is now an opportunity for you to have your say about any of the proposed new parking restrictions. Whether it is an objection, an expression of support or any other comment, please let us know what you think by filling in the online feedback form.  Alternatively, if you prefer, you can send a letter with your comments to Runnymede 2026 Parking Review, Traffic Enforcement and Parking Team, Hazel House, Merrow Lane, Guildford GU4 7BQ.",
    "Please note that the closing date for the advertising period is Friday 27 November, so please make sure we have heard from you by then.",
    "After the advertising period has ended, all the feedback received will be compiled into a report and distributed to the Parking and Traffic Enforcement Manager and county councillors.",
]


# Approximate (longitude, latitude) per proposal. Most come from OpenStreetMap
# street geocoding; entries marked "estimated" could not be found and are guesses.
COORDS = {
    "corrie-bois-hall": (-0.48382, 51.37112),
    "chapel-park-chapel-grove": (-0.49613, 51.37365),
    "green-lane-rickman-crescent": (-0.49383, 51.37484),
    "hamm-moor-lane": (-0.47502, 51.37202),
    "ledger-drive-rudge-rise": (-0.49350, 51.37150),  # estimated
    "lime-grove-sumner-place": (-0.50122, 51.36955),
    "sayes-court-farm-drive": (-0.49434, 51.36674),
    "essex-close": (-0.48782, 51.37064),
    "school-lane": (-0.50249, 51.37212),
    "bridge-road": (-0.49086, 51.38957),
    "fordwater-road": (-0.49468, 51.38622),
    "paddocks-way": (-0.49612, 51.38651),
    "station-road": (-0.50425, 51.38531),
    "windsor-street": (-0.50481, 51.39264),
    "little-green-lane": (-0.51654, 51.37698),
    "boscombe-close": (-0.53397, 51.41946),
    "claremont-road": (-0.52462, 51.43288),
    "roundway": (-0.54700, 51.42900),  # estimated
    "vicarage-road-vicarage-avenue": (-0.53689, 51.42877),
    "central-englefield-green-permit-scheme": (-0.56699, 51.42984),
    "armstrong-road": (-0.57032, 51.42801),
    "middle-hill-permit-bays": (-0.56092, 51.42980),
    "middle-hill-spencer-gardens": (-0.56142, 51.42990),
    "middle-hill-lodge-close": (-0.56042, 51.42970),
    "the-retreat": (-0.56288, 51.42943),
    "st-judes-road-west-tro-amendment": (-0.57312, 51.43049),
    "st-judes-road-east-tro-amendment": (-0.57292, 51.43039),
    "victoria-street-tro-amendment": (-0.57039, 51.42909),
    "wick-road": (-0.58124, 51.42157),
    "barnway": (-0.57017, 51.43065),
    "spring-rise": (-0.55690, 51.42871),
    "denham-road-tro-amendment": (-0.54327, 51.43371),
    "bousley-rise": (-0.52360, 51.36054),
    "brox-road": (-0.53530, 51.35515),
    "crabtree-road": (-0.53170, 51.41506),
    "stroude-road-luddington-avenue": (-0.55600, 51.40050),  # estimated
    "woodham-lane-new-haw": (-0.49914, 51.34914),
    "woodham-lane-hawthorn-way": (-0.49312, 51.35133),
    "woodham-lane-mayfield-avenue": (-0.49323, 51.35016),
    "woodham-lane-woodham": (-0.50313, 51.34741),
}


MAP_HEAD = """  <link rel="stylesheet" href="assets/vendor/maplibre-gl.css">
  <script src="assets/vendor/maplibre-gl.js"></script>"""

MAP_SCRIPT = """  <script>
    const proposals = __DATA__;
    const map = new maplibregl.Map({
      container: "proposal-map",
      center: [-0.52, 51.39],
      zoom: 10.5,
      style: {
        version: 8,
        sources: {
          osm: {
            type: "raster",
            tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
            tileSize: 256,
            maxzoom: 19,
            attribution: "&copy; <a href=\\"https://www.openstreetmap.org/copyright\\">OpenStreetMap</a> contributors"
          }
        },
        layers: [{ id: "osm", type: "raster", source: "osm" }]
      }
    });
    map.addControl(new maplibregl.NavigationControl());

    const bounds = new maplibregl.LngLatBounds();
    for (const feature of proposals.features) {
      const { title, url, drawings } = feature.properties;
      const popup = new maplibregl.Popup({ offset: 25 });
      const content = document.createElement("div");
      const link = document.createElement("a");
      link.href = url;
      link.textContent = title;
      const note = document.createElement("div");
      note.textContent = "Drawing " + drawings;
      content.append(link, note);
      popup.setDOMContent(content);
      new maplibregl.Marker({ color: "#075b8d" })
        .setLngLat(feature.geometry.coordinates)
        .setPopup(popup)
        .addTo(map);
      bounds.extend(feature.geometry.coordinates);
    }
    map.fitBounds(bounds, { padding: 40, duration: 0 });
  </script>"""


def proposals_geojson():
    features = [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": list(COORDS[p["id"]])},
            "properties": {
                "title": p["title"],
                "url": f"proposals/{p['id']}.html",
                "drawings": ", ".join(p["drawings"]),
            },
        }
        for p in PROPOSALS
    ]
    return json.dumps({"type": "FeatureCollection", "features": features})


def page_shell(title, content, depth=0, head_extra="", body_extra=""):
    prefix = "../" * depth
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)} | Runnymede Parking Review 2026</title>
  <link rel="stylesheet" href="{prefix}styles.css">
{head_extra}
</head>
<body>
  <header class="site-header">
    <a class="site-title" href="{prefix}index.html">Runnymede Parking Review 2026</a>
  </header>
  <main>
{content}
  </main>
{body_extra}
</body>
</html>
"""


def paragraph(text):
    if text.startswith("- "):
        return f"<li>{escape(text[2:])}</li>"
    return f"<p>{escape(text)}</p>"


def render_details(items):
    output = []
    bullet_items = []
    for item in items:
        if item.startswith("- "):
            bullet_items.append(item[2:])
        else:
            if bullet_items:
                output.append("<ul>")
                output.extend(f"<li>{escape(value)}</li>" for value in bullet_items)
                output.append("</ul>")
                bullet_items.clear()
            output.append(paragraph(item))
    if bullet_items:
        output.append("<ul>")
        output.extend(f"<li>{escape(value)}</li>" for value in bullet_items)
        output.append("</ul>")
    return "\n".join(output)


def render_feedback(text):
    linked_text = escape(text).replace(
        "online feedback form",
        f'<a href="{FORM_URL}">online feedback form</a>',
    )
    return f"      <p>{linked_text}</p>"


def build():
    area_by_id = {slug: (name, subtitle) for slug, name, subtitle in AREAS}
    for folder in ("areas", "proposals"):
        (ROOT / folder).mkdir(exist_ok=True)

    intro_cards = []
    for slug, name, subtitle in AREAS:
        count = sum(proposal["area"] == slug for proposal in PROPOSALS)
        intro_cards.append(
            f'<article class="card"><h2><a href="areas/{slug}.html">{escape(name)}</a></h2>'
            f"<p>{escape(subtitle)} · {count} proposals</p></article>"
        )
    index_content = f"""    <h1>Runnymede Parking Review 2026</h1>
    <p class="lead">Explore the proposed parking changes by area. Each proposal page includes its details, the associated drawing and a link to the online feedback form.</p>
    <p>The proposals are part of Surrey County Council's Runnymede parking review. The information below is based on the published <a href="{STATEMENT_URL}">Statement of Reasons</a> and its associated drawing packs.</p>
    <section aria-labelledby="map-heading">
      <h2 id="map-heading">Map of proposals</h2>
      <p>Markers show the approximate location of each proposal. Select a marker, then follow the link to open the proposal.</p>
      <div id="proposal-map" class="proposal-map" role="region" aria-label="Map of proposal locations"></div>
    </section>
    <section aria-labelledby="areas-heading">
      <h2 id="areas-heading">Choose an area</h2>
      <div class="card-list">
        {"".join(intro_cards)}
      </div>
    </section>
    <p><a href="{FORM_URL}">Go to the online feedback form</a></p>"""
    (ROOT / "index.html").write_text(
        page_shell(
            "Runnymede Parking Review 2026",
            index_content,
            head_extra=MAP_HEAD,
            body_extra=MAP_SCRIPT.replace("__DATA__", proposals_geojson().replace("</", "<\\/")),
        ),
        encoding="utf-8",
    )

    for slug, name, subtitle in AREAS:
        proposals = [proposal for proposal in PROPOSALS if proposal["area"] == slug]
        proposal_links = "\n".join(
            f'<li><a href="../proposals/{proposal["id"]}.html">{escape(proposal["title"])}</a>'
            f" <span>({escape(', '.join(proposal['drawings']))})</span></li>"
            for proposal in proposals
        )
        content = f"""    <nav class="breadcrumbs" aria-label="Breadcrumb"><a href="../index.html">Home</a> / {escape(name)}</nav>
    <h1>{escape(name)}</h1>
    <p class="lead">{escape(subtitle)}. Select a proposal to read its details and view the associated drawing.</p>
    <section class="panel" aria-labelledby="proposals-heading">
      <h2 id="proposals-heading">Proposals</h2>
      <ul class="proposal-list">
        {proposal_links}
      </ul>
    </section>
    <p><a href="{FORM_URL}">Online feedback form</a></p>"""
        (ROOT / "areas" / f"{slug}.html").write_text(
            page_shell(name, content, depth=1), encoding="utf-8"
        )

    for proposal in PROPOSALS:
        area_name, _ = area_by_id[proposal["area"]]
        map_sections = []
        for filename, page_number, drawing in proposal["maps"]:
            src = f"../assets/maps/{filename}#page={page_number}&view=FitH"
            map_sections.append(
                f"""      <section aria-labelledby="map-{page_number}-{escape(re.sub(r'[^a-zA-Z0-9]+', '-', filename))}">
        <h3 id="map-{page_number}-{escape(re.sub(r'[^a-zA-Z0-9]+', '-', filename))}">Drawing {escape(drawing)}</h3>
        <iframe class="map-frame" title="Drawing {escape(drawing)} for {escape(proposal['title'])}" src="{src}"></iframe>
        <p class="map-links"><a href="{src}" target="_blank" rel="noopener">Open drawing {escape(drawing)} in a new tab</a></p>
      </section>"""
            )
        details = render_details(proposal["details"])
        feedback = "\n".join(render_feedback(text) for text in FEEDBACK_TEXT)
        map_sections_html = "\n      ".join(map_sections)
        content = f"""    <nav class="breadcrumbs" aria-label="Breadcrumb"><a href="../index.html">Home</a> / <a href="../areas/{proposal["area"]}.html">{escape(area_name)}</a> / {escape(proposal["title"])}</nav>
    <h1>{escape(proposal["title"])}</h1>
    <p><strong>Area:</strong> {escape(proposal["division"])} · <strong>Drawing:</strong> {escape(", ".join(proposal["drawings"]))}</p>
    <section class="panel" aria-labelledby="details-heading">
      <h2 id="details-heading">Proposal details</h2>
      {details}
    </section>
    <section aria-labelledby="maps-heading">
      <h2 id="maps-heading">Associated map or diagram</h2>
      {map_sections_html}
    </section>
    <footer class="site-footer">
      <p>Source: Surrey County Council's <a href="{STATEMENT_URL}">Statement of Reasons</a> and associated drawings.</p>
    </footer>
    <section class="feedback" aria-labelledby="feedback-heading">
      <h2 id="feedback-heading">Have your say</h2>
      <p><a href="{FORM_URL}">Complete the online feedback form</a></p>
{feedback}
    </section>
"""
        (ROOT / "proposals" / f"{proposal['id']}.html").write_text(
            page_shell(proposal["title"], content, depth=1), encoding="utf-8"
        )


if __name__ == "__main__":
    build()
