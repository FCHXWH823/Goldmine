// Simple counter example for testing static analysis

module counter (
    input wire clk,
    input wire rst,
    input wire enable,
    output reg [7:0] count
);

    reg [7:0] next_count;
    
    // Combinational logic for next count
    always @(*) begin
        if (enable)
            next_count = count + 8'd1;
        else
            next_count = count;
    end
    
    // Sequential logic for counter
    always @(posedge clk or posedge rst) begin
        if (rst)
            count <= 8'd0;
        else
            count <= next_count;
    end

endmodule
