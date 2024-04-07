# Characteristics of (energy) technologies

This section defines variables and indicators related to characteristics and
specifications of (energy) technologies including power plants, transmission
lines and pipelines.

Note that there is no clear distinction whether a variable defined in this
section is an assumption (input) or a model result (output) - this depends
on the context of the modelling framework.
For example, the "installed capacity" of a power plant
may be an exogenous assumption in a (short-term) power-system dispatch model
or a result from a long-term investment model.
The respective use case should be clearly specified in the model documentation.

Explanations of the different categories and the structures
of the variables are given below.
See [technologies.yaml](technologies.yaml) for the full codelist.

## Installed Capacity

Variables for the installed capacity of (energy) production/generation
or transmission should follow the structure below.

- `Capacity|{Production type}|{Fuel}`
- `Capacity|{Production type}|{Fuel}|{Specification}`
- `Capacity|{Production type}|{Fuel}|{Specification}|{Identifier Of A Specific Power Plant}`

where `{Production type}` is one of the following:
- `Electricity`
- `Heat`
- `Hydrogen`
- `Liquids`
- `Gases`

There are also special cases that deviate from the format above, such as
specifying sectors or technology subtypes, for example
`Capacity|Heat|Residential and Commercial|{Fuel}` for heating capacity using a
given fuel type in residential and commercial buildings. See the .yaml files for
details.

Note added for IAM COMPACT: This category is used for the total capacity (the
installed base) in a given year, not for the capacity added in a given year.

# Added Capacity

Variables for the capacity added in a given year should follow the structure
below.

- `Capacity Addtions|{Production type}|{Fuel}`
- `Capacity Addtions|{Production type}|{Fuel}|{Specification}`
- `Capacity Addtions|{Production type}|{Fuel}|{Specification}|{Identifier Of A Specific Power Plant}`

Note for IAM COMPACT: These variables are not present in the original variable
list from openENTRANCE, but are included in the variable list for IPCC AR6, and
used in several models in IAM COMPACT.

## Capital Cost

Variables for the overnight capital cost for new construction of power plants
or tranmission lines should follow the structure below.

- `Capital Cost|{Fuel}|{Specification}`
- `Capital Cost|{Fuel}|{Specification}|{Identifier Of A Specific Power Plant}`

Note that it usually does not make sense to report capital costs
at a more aggregate level (i.e., `Capital Cost|{Fuel}`).

## Investment expenditure

Variables for the expenditure for new construction of power plants
or tranmission lines should follow the structure below.

- `Investment|{Type}`
- `Investment|{Type}|{Fuel}`
- `Investment|{Type}|{Fuel}|{Specification}`
