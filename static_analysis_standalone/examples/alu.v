// Simple ALU example for testing static analysis

module simple_alu (
    input wire [7:0] a,
    input wire [7:0] b,
    input wire [1:0] op,
    output reg [7:0] result
);

    always @(*) begin
        case (op)
            2'b00: result = a + b;  // Addition
            2'b01: result = a - b;  // Subtraction
            2'b10: result = a & b;  // AND
            2'b11: result = a | b;  // OR
            default: result = 8'd0;
        endcase
    end

endmodule
