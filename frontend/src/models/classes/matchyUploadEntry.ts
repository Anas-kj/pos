import { Cell } from "src/libs/matchy/src/models/classes/cell";
import { UploadEntry } from "src/libs/matchy/src/models/classes/uploadEntry";

export class MatchyUploadEntry extends UploadEntry{
    forceUpload: boolean = false;

    constructor(lines: {[key: string]: Cell} [], forceUpload: boolean) {
        super(lines);
        this.lines = lines.map(line => {
            const converted: {[key: string]: {value: string, rowIndex: number, colIndex: number}} = {};
            for (const [key, cell] of Object.entries(line)) {
                converted[key] = {
                    value: String(cell.value || ''),
                    rowIndex: Number(cell.rowIndex),
                    colIndex: Number(cell.colIndex)
                };
            }
            return converted;
        });
        
        this.forceUpload = forceUpload
    }
}