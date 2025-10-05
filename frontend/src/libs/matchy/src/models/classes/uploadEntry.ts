import { Cell } from "./cell.js";

export class UploadEntry {
    lines: {[key: string]: Cell;} [] = [];

    constructor(lines: {[key: string]: Cell;} []) {
        this.lines = lines
    }
}