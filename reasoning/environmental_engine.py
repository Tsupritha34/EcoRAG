def generate_recommendations(metrics):
    recommendations = []

    soil = metrics.get("soil", {})
    land = metrics.get("land", {})
    biodiversity = metrics.get("biodiversity", {})
    climate = metrics.get("climate", {})
    human = metrics.get("human_impact", {})

    soc = soil.get("organic_carbon")
    moisture = soil.get("moisture")

    rainfall = climate.get("annual_rainfall")
    rainfall_category = climate.get("rainfall_category")
    region_type = climate.get("region_type")

    crop = land.get("crop")
    land_use = land.get("land_use")
    tree_cover = land.get("tree_cover")

    species_richness = biodiversity.get("species_richness")

    pollution = human.get("pollution")
    pesticide = human.get("pesticide_use")

    # ---------------------------------------------------------
    # Determine whether rainfall conditions are dry
    # ---------------------------------------------------------

    low_rainfall = False

    if rainfall is not None and rainfall < 800:
        low_rainfall = True

    if rainfall_category == "low":
        low_rainfall = True

    if region_type == "semi-arid":
        low_rainfall = True

    # ---------------------------------------------------------
    # Rule 1:
    # Very low SOC + low rainfall + monoculture crop
    # ---------------------------------------------------------

    if (
        soc is not None
        and soc < 0.8
        and low_rainfall
        and crop is not None
    ):

        action = (
            "Introduce a drought-tolerant legume intercrop or seasonal "
            "cover crop with wheat, while retaining suitable crop residues "
            "on the soil."
        )

        reasoning = (
            "The SOC value of "
            f"{soc}% indicates a low-carbon soil condition for this "
            "decision rule. Combining crop diversification with additional "
            "plant biomass can increase carbon inputs, support soil organisms, "
            "and improve ground cover. Under low-rainfall conditions, keeping "
            "the soil covered can also reduce evaporation and erosion."
        )

        measurable = [
            (
                "SOC monitoring: measure SOC using the same sampling depth "
                "and laboratory method at baseline and at least annually."
            ),
            (
                "Literature benchmark: cover-crop systems showed a mean SOC "
                "stock increase of about 0.32 ± 0.08 Mg C/ha/year in a "
                "global meta-analysis."
            ),
            (
                "Do not convert that stock change directly into a percentage "
                "change in SOC concentration without soil bulk density and "
                "sampling depth."
            ),
        ]

        references = [
            (
                "Poeplau, C. & Don, A. (2015). "
                "Carbon sequestration in agricultural soils via cultivation "
                "of cover crops – A meta-analysis. "
                "Agriculture, Ecosystems & Environment, 200, 33–41. "
                "DOI: 10.1016/j.agee.2014.10.024"
            ),
        ]

        recommendations.append(
            {
                "action": action,
                "reasoning": reasoning,
                "metrics": [
                    "Soil Organic Carbon",
                    "Soil Moisture",
                    "Vegetation Diversity",
                    "Soil Biological Activity",
                    "Species Richness",
                ],
                "time_horizon": "1–3 years",
                "confidence": "High",
                "measurable_targets": measurable,
                "scientific_references": references,
            }
        )

    # ---------------------------------------------------------
    # Rule 2:
    # Monoculture + low biodiversity information
    # Recommend diversification
    # ---------------------------------------------------------

    if (
        land_use == "monoculture"
        and crop is not None
    ):

        action = (
            "Diversify the wheat system with a suitable legume intercrop, "
            "rotational crop, flowering border, or seasonal cover crop."
        )

        reasoning = (
            "A monoculture provides relatively uniform vegetation and "
            "resource availability. Increasing plant and habitat diversity "
            "can support a wider range of beneficial organisms and "
            "ecosystem functions."
        )

        measurable = [
            (
                "Record plant and animal species richness using the same "
                "sampling area and survey method each season."
            ),
            (
                "Global meta-analysis benchmark: diversified farming systems "
                "had 26% higher overall species richness on average than "
                "simplified farming systems."
            ),
            (
                "The 26% value is a population-level research estimate, "
                "not a guaranteed increase for this field."
            ),
        ]

        references = [
            (
                "Diversification and biodiversity evidence: "
                "global meta-analysis of 161 peer-reviewed articles "
                "reported 26% higher overall species richness in "
                "diversified farming systems."
            ),
            (
                "Tamburini, G. et al. (2020). "
                "Agricultural diversification promotes multiple ecosystem "
                "services without compromising yield. "
                "Science Advances, 6(47), eaba1715. "
                "DOI: 10.1126/sciadv.aba1715"
            ),
        ]

        recommendations.append(
            {
                "action": action,
                "reasoning": reasoning,
                "metrics": [
                    "Species Richness",
                    "Vegetation Diversity",
                    "Habitat Diversity",
                    "Pollinator Abundance",
                ],
                "time_horizon": "1–3 years",
                "confidence": "Medium-High",
                "measurable_targets": measurable,
                "scientific_references": references,
            }
        )

    # ---------------------------------------------------------
    # Rule 3:
    # Low tree cover
    # ---------------------------------------------------------

    if (
        tree_cover is not None
        and tree_cover < 15
    ):

        action = (
            "Establish locally suitable native tree and shrub strips "
            "along field boundaries or as habitat corridors, while "
            "checking water requirements before planting."
        )

        reasoning = (
            "Low tree cover can limit vertical habitat structure and "
            "connectivity. Native trees and shrubs can add shelter, "
            "food resources, nesting opportunities, and movement pathways."
        )

        measurable = [
            (
                "Measure tree and shrub cover annually using the same "
                "mapped field boundaries."
            ),
            (
                "Track the number of native plant species established "
                "and the number of observed bird and insect taxa."
            ),
            (
                "Use species-richness and vegetation-cover trends as "
                "field-level indicators rather than assuming a fixed "
                "biodiversity gain."
            ),
        ]

        references = [
            (
                "Torralba, M. et al. (2016). "
                "Do European agroforestry systems enhance biodiversity "
                "and ecosystem services? A meta-analysis. "
                "Agriculture, Ecosystems & Environment, 230, 150–161. "
                "DOI: 10.1016/j.agee.2016.06.002"
            ),
        ]

        recommendations.append(
            {
                "action": action,
                "reasoning": reasoning,
                "metrics": [
                    "Tree Cover",
                    "Habitat Diversity",
                    "Species Richness",
                    "Vegetation Diversity",
                ],
                "time_horizon": "2–5 years",
                "confidence": "Medium",
                "measurable_targets": measurable,
                "scientific_references": references,
            }
        )

    # ---------------------------------------------------------
    # Rule 4:
    # Low soil moisture
    # ---------------------------------------------------------

    if (
        moisture is not None
        and moisture < 20
    ):

        action = (
            "Use organic mulch, retain crop residues, and maintain "
            "appropriate ground cover to reduce soil moisture loss."
        )

        reasoning = (
            "Ground cover reduces direct soil exposure and can reduce "
            "evaporation and erosion. Organic residues also add carbon "
            "inputs as they decompose."
        )

        measurable = [
            (
                "Measure soil moisture at fixed locations and consistent "
                "times before and after management changes."
            ),
            (
                "Compare seasonal minimum soil moisture between treated "
                "and baseline areas."
            ),
        ]

        references = [
            (
                "Tamburini, G. et al. (2020). "
                "Agricultural diversification promotes multiple ecosystem "
                "services without compromising yield. "
                "Science Advances, 6(47), eaba1715."
            ),
        ]

        recommendations.append(
            {
                "action": action,
                "reasoning": reasoning,
                "metrics": [
                    "Soil Moisture",
                    "Soil Organic Carbon",
                    "Soil Biological Activity",
                ],
                "time_horizon": "Weeks–Months",
                "confidence": "High",
                "measurable_targets": measurable,
                "scientific_references": references,
            }
        )

    # ---------------------------------------------------------
    # Rule 5:
    # Pollution or pesticide pressure
    # ---------------------------------------------------------

    if (
        pollution in ["medium", "high"]
        or pesticide in ["medium", "high"]
    ):

        action = (
            "Create vegetated buffer zones and use Integrated Pest "
            "Management (IPM) to reduce unnecessary chemical exposure."
        )

        reasoning = (
            "Vegetated buffers can reduce sediment and pollutant movement, "
            "while IPM reduces unnecessary pesticide applications and "
            "can protect non-target organisms."
        )

        measurable = [
            "Track pesticide applications per hectare.",
            "Monitor pollinator observations using a consistent survey method.",
            "Measure water-quality indicators where runoff is a concern.",
        ]

        references = [
            (
                "Tamburini, G. et al. (2020). "
                "Agricultural diversification promotes multiple ecosystem "
                "services without compromising yield. "
                "Science Advances, 6(47), eaba1715."
            ),
        ]

        recommendations.append(
            {
                "action": action,
                "reasoning": reasoning,
                "metrics": [
                    "Pollution",
                    "Water Quality",
                    "Pollinator Abundance",
                    "Beneficial Insect Diversity",
                ],
                "time_horizon": "Months–2 years",
                "confidence": "Medium-High",
                "measurable_targets": measurable,
                "scientific_references": references,
            }
        )

    # ---------------------------------------------------------
    # Default rule
    # ---------------------------------------------------------

    if not recommendations:

        recommendations.append(
            {
                "action": (
                    "Collect baseline measurements for SOC, soil moisture, "
                    "rainfall, vegetation diversity, and species richness "
                    "before selecting a targeted intervention."
                ),
                "reasoning": (
                    "A multi-metric baseline makes it possible to compare "
                    "changes over time and avoid drawing conclusions from "
                    "a single environmental indicator."
                ),
                "metrics": [
                    "Soil Organic Carbon",
                    "Soil Moisture",
                    "Rainfall",
                    "Vegetation Diversity",
                    "Species Richness",
                ],
                "time_horizon": "Short-term assessment",
                "confidence": "Low-Medium",
                "measurable_targets": [
                    "Establish baseline measurements for each available metric.",
                    "Repeat measurements using consistent methods and locations.",
                ],
                "scientific_references": [],
            }
        )

    return recommendations