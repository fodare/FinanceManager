using AutoMapper;
using backend.Dtos;
using backend.Helpers;
using backend.Models;
using backend.Services;
using Microsoft.AspNetCore.Mvc;

namespace backend.Controllers
{
    [ApiController]
    [Route("api/v3/[controller]")]
    public class RecordController : ControllerBase
    {
        private readonly IRecordService _recordService;
        IMapper _mapper;
        private readonly RecrodsHelper _recordHelper;
        public RecordController(IRecordService recordService)
        {
            _recordService = recordService;
            _recordHelper = new RecrodsHelper();
            _mapper = new Mapper(new MapperConfiguration(cfg =>
            {
                cfg.CreateMap<RecordModel, GetRecordDTO>().ReverseMap();
            }));
        }

        [HttpGet("/recordService", Name = "RecordServiceHome")]
        public ActionResult GetRecordServiceHealth()
        {
            return Ok(DateTime.Now);
        }

        [HttpPost("createRecord", Name = "AddRecord")]
        public ActionResult<ResponseModel<string>> AddNewRecord([FromBody] CreateRecordDTO newRecord)
        {
            ResponseModel<string> response = new();
            bool isUserAdded = _recordService.CreateRecord(newRecord);
            if (!isUserAdded)
            {
                response.Message = "Error creating user. Please try again.";
                return BadRequest(response);
            }
            response.Message = "Record created succeffully!";
            response.Success = true;
            return Ok(response);
        }

        [HttpGet("records", Name = "GetRecords")]
        public ActionResult<ResponseModel<GetRecordDTO>> FetchRecords()
        {
            ResponseModel<GetRecordDTO> response = new();
            GetRecordDTO recordsInfo = new();
            var recordList = _recordService.GetRecords();
            if (recordList is null)
            {
                response.Message = "Error fetching records. Please try again";
                return BadRequest(response);
            }

            recordsInfo.CreditTotal = _recordHelper.CalculateCreditSum(recordList);
            recordsInfo.DebitTotal = _recordHelper.CalculateDebitSum(recordList);
            recordsInfo.Records = recordList;

            response.Message = "Successfully retrived records.";
            response.Success = true;
            response.Data = recordsInfo;
            return Ok(response);
        }

        [HttpGet("{recordId}", Name = "GetRecordById")]
        public ActionResult<ResponseModel<RecordModel>> GetRecordById(int recordId)
        {
            ResponseModel<RecordModel> response = new();
            var queridRecord = _recordService.GetRecordById(recordId);
            if (queridRecord is null)
            {
                response.Message = $"Error fetching record Id {recordId}. Please try again!";
                return BadRequest(response);
            }
            response.Success = true;
            response.Message = "Record retrived successfully!";
            response.Data = queridRecord;
            return Ok(response);
        }

        [HttpPost("byDateRange", Name = "GetRecordsByDateRange")]
        public ActionResult<ResponseModel<GetRecordDTO>> GetRecordsByDate(FilterByDateDTO range)
        {
            ResponseModel<GetRecordDTO> response = new();
            GetRecordDTO recordsInfo = new();
            var recordList = _recordService.GetRecordsByDateRange(range.StartDate, range.EndDate);
            if (recordList is null)
            {
                response.Message = $"Can not find records from {range.StartDate} - {range.EndDate}";
                return BadRequest(response);
            }

            recordsInfo.CreditTotal = _recordHelper.CalculateCreditSum(recordList);
            recordsInfo.DebitTotal = _recordHelper.CalculateDebitSum(recordList);
            recordsInfo.Records = recordList;

            response.Message = "Successfully retrived records";
            response.Success = true;
            response.Data = recordsInfo;
            return Ok(response);
        }

        [HttpPut("updateRecord/{id}", Name = "UpdateRecord")]
        public ActionResult<ResponseModel<string>> ReplaceRecord(UpdateRecordDTO updatedRecord, int id)
        {
            ResponseModel<string> response = new();
            bool recordUpdated = _recordService.UpdateRecord(id, updatedRecord);
            if (!recordUpdated)
            {
                response.Message = "Error updating record. Please try again";
                return BadRequest(response);
            }
            response.Success = true;
            response.Message = $"Successfuly updated record id {id}";
            return Ok(response);
        }
    }
}