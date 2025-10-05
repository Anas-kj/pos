export enum ContractType {
    Cdi = "Cdi",
    Cdd = "Cdd",
    Sivp = "Sivp",
    Apprenti = "Apprenti",
}

export const contract_types = [
    {value: null, view_value: "No Contract"},
    { value: ContractType.Cdi, view_value: "CDI"},
    { value: ContractType.Cdd, view_value: "CDD"},
    { value: ContractType.Sivp, view_value: "SIVP"},
    { value: ContractType.Apprenti, view_value: "Apprenti"},
];