export enum ContractType {
    cdi = "cdi",
    cdd = "cdd",
    sivp = "sivp",
    apprenti = "apprenti",
}

export const contract_types = [
    {value: null, view_value: "No Contract"},
    { value: ContractType.cdi, view_value: "CDI"},
    { value: ContractType.cdd, view_value: "CDD"},
    { value: ContractType.sivp, view_value: "SIVP"},
    { value: ContractType.apprenti, view_value: "Apprenti"},
];