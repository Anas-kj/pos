import { PaginationFilter } from "./paginationFilter";

export class EmployeeFilter extends PaginationFilter {
    name_substr: string | undefined;

    constructor(name_substr: string | undefined = "", page_number: number = 1, page_size: number = 10) {
        super(page_number, page_size);
        this.name_substr = name_substr;
    }

}
