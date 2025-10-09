import { Cell } from "src/libs/matchy/src/models/classes/cell";

export interface MatchyUploadEntry {
    lines: {[key: string]: Cell;} [];
    forceUpload: boolean | false;
}