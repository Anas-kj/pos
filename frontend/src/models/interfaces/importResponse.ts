import { BaseOut } from "./baseOut";
import { MatchyWrongCells } from "./matchyWrongCells";

export interface importResponse extends BaseOut {
    errors?: string;
    warnings?: string;
    wrong_cells?: MatchyWrongCells[];
}